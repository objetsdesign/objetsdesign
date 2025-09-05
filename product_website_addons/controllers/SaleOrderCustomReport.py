from odoo import http, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SaleOrderCustomReport(http.Controller):

    @http.route(['/my/orders/<int:order_id>/custom_report'], type='http', auth="public", website=True)
    def custom_sale_order_report(self, order_id, **kwargs):
        sale_order = request.env['sale.order'].sudo().browse(order_id)
        pdf_content, _ = request.env.ref('sale.action_report_saleorder').sudo()._render_qweb_pdf([order_id])

        pdf_headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
        ]
        return request.make_response(pdf_content, headers=pdf_headers)
