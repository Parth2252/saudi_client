# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request

class SetMailServer(http.Controller):

    @http.route('/get_selected_mail_server', type='json', auth="public", methods=['POST'], website=True)
    def get_selected_mail_server(self, **post):
        return "by_company" if request.env.user.is_mail_by_company else "by_user"

    @http.route(['/select_mail_server'], type='json', auth='public')
    def user_selected_language(self, selected_mail_server):
        if selected_mail_server == "by_user":
            request.env.user.is_mail_by_company = False
        if selected_mail_server == "by_company":
            request.env.user.is_mail_by_company = True
