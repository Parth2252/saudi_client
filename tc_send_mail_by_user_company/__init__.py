# -*- coding: utf-8 -*-
from . import models
from . import controllers


def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import UserError
    version_info = common.exp_version()
    server_series = version_info.get('server_serie')
    if server_series != '18.0':
        raise UserError('Module support Odoo series 18.0 found {}.'.format(server_series))
    return True
