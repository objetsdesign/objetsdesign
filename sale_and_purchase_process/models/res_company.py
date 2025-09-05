from odoo import models, fields, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    purchase_process_status = fields.Selection([
        ('od', 'Objet Design'),
        ('bsi', 'BSI'),
        ('von_ros', 'Von Ros Industry'),
    ], string="Default Purchase Status", default='od')
