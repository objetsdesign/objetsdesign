from odoo import http
from odoo.http import request

class WebsiteSaleVariant(http.Controller):

    @http.route('/shop/get_variant_default_code', type='json', auth='public', website=True)
    def get_variant_default_code(self, product_id):
        product = request.env['product.product'].sudo().browse(product_id)
        return {'default_code': product.default_code or ''}
