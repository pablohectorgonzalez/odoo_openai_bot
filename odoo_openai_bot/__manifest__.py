{
    'name': 'Odoo OpenAI Bot',
    'version': '17.0.1.0.0',
    'summary': 'Integración básica de OpenAI para respuestas en Discuss/Chatter',
    'description': 'Módulo que permite llamar a OpenAI desde Odoo y publicar respuestas en canales de Discuss.',
    'author': 'Tu Nombre',
    'category': 'Tools',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'views/openai_settings_views.xml',
        'security/ir.model.access.csv',
        'data/odoo_openai_cron.xml',
        'data/odoo_openai_processed_model.xml',
    ],
    'installable': True,
    'application': False,
}
