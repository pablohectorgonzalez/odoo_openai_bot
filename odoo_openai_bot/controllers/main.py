# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class OpenAIBotController(http.Controller):
    @http.route('/openai_bot/webhook', type='json', auth='user', methods=['POST'], csrf=False)
    def webhook(self, **post):
        # POST JSON expected: {"channel_id": <id>, "text": "..."}
        channel_id = post.get('channel_id')
        text = post.get('text')
        if not channel_id or not text:
            return {"error": "Falta channel_id o text"}
        bot = request.env['odoo.openai.bot'].sudo()
        try:
            reply = bot.handle_user_message(channel_id=channel_id, user_text=text)
            return {"ok": True, "reply": reply}
        except Exception as e:
            return {"ok": False, "error": str(e)}
