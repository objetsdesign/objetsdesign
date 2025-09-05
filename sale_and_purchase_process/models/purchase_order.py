from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    process_status = fields.Selection([
        ('od', 'Objet Design'),
        ('bsi', 'BSI'),
        ('von_ros', 'Von Ros Industry'),
    ], string='Process Status', tracking=True)
    purchase_category = fields.Selection([
        ('od_tunisie', 'OD → Tunisie'),
        ('od_asie', 'OD → Asie'),
    ], string='Catégorie d’achat', tracking=True, default='od_tunisie')
    customer_id = fields.Many2one('res.partner', string='Client')
    sale_id = fields.Many2one('sale.order', string='Commande Client')

    def create(self, vals):
        # Si aucun statut choisi → on prend celui configuré dans la société
        if not vals.get('process_status') and vals.get('company_id'):
            company = self.env['res.company'].browse(vals['company_id'])
            if company.purchase_process_status:
                vals['process_status'] = company.purchase_process_status
        return super().create(vals)


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_process_status = fields.Selection([
        ('od', 'OD'),
        ('bsi', 'BSI'),
        ('von_ros', 'Von Ros Industry'),
    ], string="Default Purchase Status", default='od')
