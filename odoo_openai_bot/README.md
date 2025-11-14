# Odoo OpenAI Bot

Módulo para Odoo 17 que integra llamadas a la API de OpenAI y publica respuestas en canales de Discuss (mail.channel).

## Instalación
1. Copia la carpeta en `addons/`.
2. Instala dependencias: `pip install -r requirements.txt`.
3. Reinicia Odoo y actualiza la lista de apps.
4. Instala el módulo.
5. Configura API Key en Settings -> OpenAI Bot.

## Uso
Llama al método `handle_user_message(channel_id, user_text)` desde Odoo shell, acciones automáticas o un controller.

## Notas de seguridad
- Guarda la API Key en `ir.config_parameter` (se hace en este módulo).
- No subas la API Key a repositorios públicos.
- Para producción, considera usar variables de entorno y restringir quién puede ver/editar el parámetro.
