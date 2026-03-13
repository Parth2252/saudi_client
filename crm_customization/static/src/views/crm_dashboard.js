/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

export class CrmDashBoard extends Component {
    static template = "crm_customization.CrmDashboard";
    static props = {
        domain: { type: Array, optional: true },
    };
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.crmData = {};

        onWillStart(async () => {
            await this.fetchDashboardData();
        });

        onWillUpdateProps(async (nextProps) => {
            if (JSON.stringify(this.props.domain) !== JSON.stringify(nextProps.domain)) {
                await this.fetchDashboardData(nextProps.domain);
            }
        });
    }

    async fetchDashboardData(domain = this.props.domain) {
        this.crmData = await this.orm.call("crm.lead", "retrieve_crm_dashboard", [], { domain });
    }

    /**
     * This method manages dashboard filters without clearing global filters like 'My Pipeline'.
     */
    setSearchContext(ev) {
        const target = ev.currentTarget || ev.target;
        const filterName = target.closest('.dash-box').getAttribute("filter_name");

        if (!filterName || !this.env.searchModel) {
            return;
        }

        const dashFilterNames = ['open_rfq', 'submitted_offer', 'order_confirmed', 'delayed_rfq'];

        // Find all search items for the dashboard
        const allDashItems = this.env.searchModel.getSearchItems((item) =>
            dashFilterNames.includes(item.name)
        );

        // Deactivate any currently active dashboard filters (so they don't stack)
        for (const item of allDashItems) {
            const isActive = this.env.searchModel.query.some(q => q.searchItemId === item.id);
            if (isActive) {
                this.env.searchModel.toggleSearchItem(item.id);
            }
        }

        // Activate the clicked dashboard filter
        const targetItems = allDashItems.filter(item => item.name === filterName);
        for (const item of targetItems) {
            this.env.searchModel.toggleSearchItem(item.id);
        }
    }
}

// List View Dashboard
export class CrmDashBoardRenderer extends ListRenderer {
    static template = "crm_customization.CrmDashboardListView";
    static components = Object.assign({}, ListRenderer.components, { CrmDashBoard });
}

export const CrmDashBoardListView = {
    ...listView,
    Renderer: CrmDashBoardRenderer,
};

registry.category("views").add("crm_dashboard_list", CrmDashBoardListView);

// Kanban View Dashboard
export class CrmDashBoardKanbanRenderer extends KanbanRenderer {
    static template = "crm_customization.CrmDashboardKanbanView";
    static components = Object.assign({}, KanbanRenderer.components, { CrmDashBoard });
}

export const CrmDashBoardKanbanView = {
    ...kanbanView,
    Renderer: CrmDashBoardKanbanRenderer,
};

registry.category("views").add("crm_dashboard_kanban", CrmDashBoardKanbanView);
