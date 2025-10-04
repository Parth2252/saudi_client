from odoo import models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        """Inherit method to enable the track inventory checkbox and set MTO & Buy routes."""
        # Get the route IDs for MTO and Buy
        mto_route = self.env.ref('stock.route_warehouse0_mto', raise_if_not_found=False)
        buy_route = self.env.ref('purchase_stock.route_warehouse0_buy', raise_if_not_found=False)

        default_routes = []
        if mto_route:
            default_routes.append(mto_route.id)
        if buy_route:
            default_routes.append(buy_route.id)

        for vals in vals_list:
            vals["is_storable"] = True
            vals["purchase_method"] = "purchase"

            if default_routes:
                if vals.get("route_ids") and isinstance(vals["route_ids"], list):
                    # Extract existing route IDs if any
                    existing_routes = []
                    for route in vals["route_ids"]:
                        if route[0] in (6, 4):  # (6, 0, [ids]) or (4, id)
                            if route[0] == 6:
                                existing_routes += route[2]
                            elif route[0] == 4:
                                existing_routes.append(route[1])
                    merged_routes = list(set(existing_routes + default_routes))
                    vals["route_ids"] = [(6, 0, merged_routes)]
                else:
                    vals["route_ids"] = [(6, 0, default_routes)]

        return super().create(vals_list)


