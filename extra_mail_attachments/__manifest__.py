# See LICENSE file for full copyright and licensing details.

{
    "name": "Extra Mail Attachments",
    "version": "18.0.0.0.0",
    "category": "Mail",
    "depends": ["mail"],
    "data": ["wizard/mail_compose_message_view.xml"],
    "assets": {
        "web.assets_backend": [
            "extra_mail_attachments/static/scss/mail_attachments.scss",
        ]
    },
    "installable": True,
    "images": ["images/extra-email.png"],
}
