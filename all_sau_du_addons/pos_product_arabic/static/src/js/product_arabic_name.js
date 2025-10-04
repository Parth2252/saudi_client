odoo.define('pos_product_arabic.pos_product_arabic_name', function (require) {
    "use strict";
    var models = require('point_of_sale.models');

    var models = require('point_of_sale.models');
models.load_fields('product.product', ['display_name','arabic_name','list_price', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id',
'barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description',
'product_tmpl_id','tracking']);


});