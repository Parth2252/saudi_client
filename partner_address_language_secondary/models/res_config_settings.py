# -*- coding: utf-8 -*-
from odoo import api, fields, models 


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    second_lang = fields.Char(string='Partner Secondary Language')

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('partner.address.language.secondary', self.second_lang)
        self.modify_partner_view()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['second_lang'] = self.env['ir.config_parameter'].sudo().get_param('partner.address.language.secondary', default=False)
        return res

    def modify_partner_view(self):
        second_lang = self.env['ir.config_parameter'].sudo().get_param('partner.address.language.secondary', default=False)

        new_arch = """
        <data>

           <xpath expr="//field[@name='parent_id']/parent::div" position="before">
               <div class="o_row">
                   <field name="name_lang2" placeholder="Name in $LANG"/>
               </div>
           </xpath>

           <field name="vat" position="before">
                <label for="street1_lang2" string="Address in $LANG"/>
                <div class="o_address_format">
                    <field name="street1_lang2" placeholder="Street in $LANG" class="o_address_street"/>
                    <field name="street2_lang2" placeholder="Street 2 in $LANG" class="o_address_street"/>
                    <field name="city_lang2" placeholder="City in $LANG" class="o_address_city"/>
                    <field name="country_lang2" placeholder="Country in $LANG" class="o_address_city"/>
                </div>
            </field>

        </data>
        """
        view_id = self.env.ref('partner_address_language_secondary.view_form_res_partner_inherit')
        view_id.arch_base = new_arch.replace('$LANG', second_lang or "Unknown Lang")

        new_arch = """
        <data>

           <xpath expr="//field[@name='name']/parent::h1" position="after">
               <div class="o_row">
                   <field name="name_lang2" placeholder="Name in $LANG"/>
               </div>
           </xpath>

           <field name="vat" position="before">
                <label for="street1_lang2" string="Address in $LANG"/>
                <div class="o_address_format">
                    <field name="street1_lang2" placeholder="Street in $LANG" class="o_address_street"/>
                    <field name="street2_lang2" placeholder="Street 2 in $LANG" class="o_address_street"/>
                    <field name="city_lang2" placeholder="City in $LANG" class="o_address_city"/>
                    <field name="country_lang2" placeholder="Country in $LANG" class="o_address_city"/>
                </div>
            </field>

        </data>
        """
        view_id = self.env.ref('partner_address_language_secondary.view_form_res_company_inherit')
        view_id.arch_base = new_arch.replace('$LANG', second_lang or "Unknown Lang")

