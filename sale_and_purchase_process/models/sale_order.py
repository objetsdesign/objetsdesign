from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    po_created = fields.Boolean(string='Commande Achat Créée', default=False)
    show_bom_button = fields.Boolean(compute='_compute_show_bom_button',default=False)
    order_type = fields.Selection(
        [('sample', 'Échantillon'), ('order', 'Commande')],
        string="Type de commande",
        default='order',
        required=True,
        help="Sélectionnez si cette commande est un échantillon ou une commande normale"
    )
    product_category_type = fields.Selection(
        [
            ('rnd', 'R&D'),
            ('standard', 'Produit Standard'),
            ('finished', 'Produit Fini')
        ],
        string="Type de produit demandé",
        default='standard',
        required=True,
        help="Spécifiez si le produit demandé est un produit en R&D, standard ou fini."
    )

    @api.depends('state', 'po_created')
    def _compute_show_bom_button(self):
        for rec in self:
            rec.show_bom_button = rec.state in ('draft', 'sent') and not rec.po_created

    def action_create_purchase(self):
        for order in self:
            if not order.po_created:
                po_lines = []
                for line in order.order_line:
                    po_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'price_unit': line.price_unit,
                    }))

                po_vals = {
                    'partner_id': order.partner_id.id,
                    'customer_id': order.partner_id.id,
                    'sale_id': order.id,
                    'purchase_category': 'od_tunisie',  # ou logique métier
                    'order_line': po_lines,
                }
                po = self.env['purchase.order'].create(po_vals)
                order.message_post(body=f"Commande Achat générée automatiquement: {po.name}")

    def action_confirm(self):
        res = super().action_confirm()
        # Appel automatique pour créer le purchase.order
        self.action_create_purchase()
        return res
