# -*- coding: utf-8 -*-
import json
import requests
from odoo import models, api, _
from odoo.exceptions import UserError

class OdooOpenAIBot(models.Model):
    _name = 'odoo.openai.bot'
    _description = 'Helpers to call OpenAI'

    @api.model
    def _get_openai_key(self):
        return self.env['ir.config_parameter'].sudo().get_param('odoo_openai_bot.api_key')

    def call_openai_chat(self, messages, model='gpt-4o-mini'):
        """messages: list of dicts [{'role':'user','content':'...'}]"""
        api_key = self._get_openai_key()
        if not api_key:
            raise UserError(_('OpenAI API key not configured'))

        url = 'https://api.openai.com/v1/chat/completions'
        payload = {
            'model': model,
            'messages': messages,
            'max_tokens': 700,
            'temperature': 0.2,
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        except Exception as e:
            raise UserError(_('Error al conectar con OpenAI: %s') % e)

        if resp.status_code != 200:
            # intenta parsear mensaje de error
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            raise UserError(_('OpenAI error: %s') % err)

        data = resp.json()
        # Adaptar según estructura (models tipo chat completions)
        content = ''
        try:
            content = data['choices'][0]['message']['content']
        except Exception:
            # fallback
            content = data.get('choices', [{}])[0].get('text', '')
        return content

    def reply_in_channel(self, channel_id, body):
        Channel = self.env['mail.channel'].sudo()
        ch = Channel.browse(int(channel_id))
        if not ch.exists():
            raise UserError(_('Canal no encontrado'))
        ch.message_post(body=body, subtype_xmlid='mail.mt_comment')

    def handle_user_message(self, channel_id, user_text):
        messages = [
            {'role': 'system', 'content': 'Eres un asistente de Odoo. Responde de forma concisa y segura.'},
            {'role': 'user', 'content': user_text},
        ]
        reply = self.call_openai_chat(messages)
        # publica la respuesta en el canal
        self.reply_in_channel(channel_id, reply)
        return reply

    @api.model
    def cron_process_new_messages(self, limit=20):
        """Cron job: busca mensajes nuevos y no procesados y responde con OpenAI.
        Para evitar duplicados, registramos los message_id procesados en el modelo odoo.openai.processed.
        """
        Message = self.env['mail.message'].sudo()
        Processed = self.env['odoo.openai.processed'].sudo()
        # Buscar mensajes que parezcan de usuarios (comentarios) y que no estén procesados
        domain = [('message_type', '=', 'comment')]
        messages = Message.search(domain, order='create_date desc', limit=limit)
        for msg in messages:
            # Evitar respuestas a mensajes generados por el bot (evita bucles)
            if msg.author_id and msg.author_id.is_system:
                continue
            # si ya procesado, saltar
            if Processed.search([('message_id', '=', msg.id)], limit=1):
                continue
            # intentamos extraer un channel_id si es un mensaje de canal
            channel_id = False
            if msg.channel_ids:
                channel = msg.channel_ids[0]
                channel_id = channel.id
            elif msg.model == 'mail.channel' and msg.res_id:
                channel_id = msg.res_id
            # si no hay canal, marcamos como procesado pero no respondemos
            if not channel_id:
                Processed.create({'message_id': msg.id})
                continue
            # Llamar a OpenAI y responder
            try:
                user_text = (msg.body or '').strip()
                if not user_text:
                    Processed.create({'message_id': msg.id})
                    continue
                messages_payload = [
                    {'role': 'system', 'content': 'Eres un asistente de Odoo. Responde de forma concisa y segura.'},
                    {'role': 'user', 'content': user_text},
                ]
                reply = self.call_openai_chat(messages_payload)
                # publicar respuesta
                self.reply_in_channel(channel_id, reply)
                # registrar como procesado
                Processed.create({'message_id': msg.id})
            except Exception as e:
                # Registrar error en logs y continuar
                _logger = self.env.context.get('logger')
                try:
                    self.env['ir.logging'].sudo().create({
                        'name': 'odoo_openai_bot',
                        'type': 'server',
                        'dbname': self.env.cr.dbname,
                        'level': 'ERROR',
                        'message': 'Error al procesar mensaje %s: %s' % (msg.id, e),
                        'path': 'odoo_openai_bot.odoo_bot.cron',
                        'func': 'cron_process_new_messages',
                    })
                except Exception:
                    pass
                # marcar procesado para evitar retries infinitos
                Processed.create({'message_id': msg.id})
                continue
