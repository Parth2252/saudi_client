# -*- coding: utf-8 -*-
{
  "name"                 :  "Outgoing Mail Server By User Or Company",
  "summary"              :  """Module allows to send mail from user or company account, smtp by company , smtp by user , outgoing mail by company , outgoing mail by users both , mail by company , mail by user""",
  "category"             :  "Mail",
  "version"              :  "1.1.0",
  "sequence"             :  7,
  "author"               :  "Titans Code Tech",
  "license"              :  "OPL-1",
  "website"              :  "https://www.titanscodetech.com",
  "description"          :  """
        This Apps allow you to config outgoing mail server by user or company""",
  "depends"              :  [
                             'mail','web','base'
                            ],
  "data"                 :  [
                             'views/configuration_view.xml',
                            ],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "assets": {    
        'web.assets_backend': [
            'tc_send_mail_by_user_company/static/src/xml/titans_switch_mail_by.xml',
            'tc_send_mail_by_user_company/static/src/js/mailsend_service.js',
            'tc_send_mail_by_user_company/static/src/js/titans_switch_mail_by.js',
        ]
    },
  "price"                :  18,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
