/** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";
import { debounce } from "@web/core/utils/timing";
import { session } from "@web/session";
import { user } from "@web/core/user";
export class TitansMailServerTemplate extends Component {
    static template = "tc_send_mail_by_user_company.titans_mail_server_template";
    static components = { Dropdown, DropdownItem};
    setup() {
        // const rpc = useService("rpc");
        this.rpc = rpc;
        this.mailsendService = useService('mailsend');
        this.userLanguageCode = session.bundle_params.lang;
        onWillStart(async () => {
            this.all_type = this.mailsendService.getType()
            this.selected_server = await this.mailsendService.getSelectedType();
            console.log("selected_server",this.selected_server)
            console.log("this.all_type",this.all_type)
        })
    }
    async _titansToggleMailClick(type) {
      this.mailsendService.setType(type);
    }
}

export const systrayItem = {
    Component: TitansMailServerTemplate,
};

registry.category("systray").add("tc_send_mail_by_user_company.TitansMailServerTemplate", systrayItem, { sequence: 1 });