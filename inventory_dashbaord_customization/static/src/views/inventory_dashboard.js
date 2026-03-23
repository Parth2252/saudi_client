/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";

export class InventoryDashBoard extends Component {
    static template = "inventory_dashbaord_customization.InventoryDashboard";
    static props = {
        context: { type: Object, optional: true },
    };

    get showReceipts() {
        const sm = this.env.searchModel;
        if (!sm) return true;
        const activeItems = sm.getSearchItems((i) => i.isActive);
        const domainStr = JSON.stringify(sm.domain || []);
        const contextStr = JSON.stringify(this.props.context || {});

        const isIncoming = activeItems.some(i => (i.name || '').includes('incoming') || (i.name || '').includes('receivable') || (i.name || '').includes('received') || (i.name || '').includes('receipt')) || domainStr.includes('incoming') || contextStr.includes('incoming');
        const isOutgoing = activeItems.some(i => (i.name || '').includes('outgoing') || (i.name || '').includes('deliver') || (i.name || '').includes('pending_grn')) || domainStr.includes('outgoing') || contextStr.includes('outgoing');

        if (isOutgoing && !isIncoming) {
            return false;
        }
        return true;
    }

    get showDeliveries() {
        const sm = this.env.searchModel;
        if (!sm) return true;
        const activeItems = sm.getSearchItems((i) => i.isActive);
        const domainStr = JSON.stringify(sm.domain || []);
        const contextStr = JSON.stringify(this.props.context || {});

        const isIncoming = activeItems.some(i => (i.name || '').includes('incoming') || (i.name || '').includes('receivable') || (i.name || '').includes('received') || (i.name || '').includes('receipt')) || domainStr.includes('incoming') || contextStr.includes('incoming');
        const isOutgoing = activeItems.some(i => (i.name || '').includes('outgoing') || (i.name || '').includes('deliver') || (i.name || '').includes('pending_grn')) || domainStr.includes('outgoing') || contextStr.includes('outgoing');

        if (isIncoming && !isOutgoing) {
            return false;
        }
        return true;
    }

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.dashboardData = {};

        onWillStart(async () => {
            this.dashboardData = await this.orm.call("stock.picking", "retrieve_dashboard");
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

export class InventoryDashBoardRenderer extends ListRenderer {
    static template = "inventory_dashbaord_customization.InventoryDashboardListView";
    static components = Object.assign({}, ListRenderer.components, { InventoryDashBoard });
}

export const InventoryDashBoardListView = {
    ...listView,
    Renderer: InventoryDashBoardRenderer,
};

registry.category("views").add("inventory_dashboard_list", InventoryDashBoardListView);
