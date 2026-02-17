/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";

export class AccountDashBoard extends Component {
    static template = "accounting_customization.AccountDashboard";
    static props = {};
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.purchaseData = {};

        onWillStart(async () => {
            this.purchaseData = await this.orm.call("account.move", "retrieve_dashboard");
        });
    }

    /**
     * This method clears the current search query and activates
     * the filters found in `filter_name` attribute from button pressed
     */
    setSearchContext(ev) {
        const filter_name = ev.currentTarget.getAttribute("filter_name");
        const filters = filter_name.split(",");
        const searchItems = this.env.searchModel.getSearchItems((item) =>
            filters.includes(item.name)
        );
        this.env.searchModel.query = [];
        for (const item of searchItems) {
            this.env.searchModel.toggleSearchItem(item.id);
        }
    }
}

export class AccountDashBoardRenderer extends ListRenderer {
    static template = "accounting_customization.AccountDashboardListView";
    static components = Object.assign({}, ListRenderer.components, { AccountDashBoard });
}

export const AccountDashBoardListView = {
    ...listView,
    Renderer: AccountDashBoardRenderer,
};

registry.category("views").add("account_dashboard_list", AccountDashBoardListView);
