from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleBomWizard(models.Model):
    _name = "sale.bom.wizard"
    _description = "Sélection des composants à acheter"

    sale_id = fields.Many2one('sale.order', string='Commande Client', readonly=True)
    bom_id=fields.Many2one('mrp.bom')
    bom_ids = fields.Many2many(
        'mrp.bom',
        'sale_bom_wizard_m2m_bom_rel',
        'wizard_id', 'bom_id',
        string='Nomenclatures',
        required=False,
    )
    order_line_ids = fields.Many2many(
        'sale.order.line',
        string="Lignes de commande",
        compute="_compute_order_lines",
        store=False
    )

    @api.depends('sale_id')
    def _compute_order_lines(self):
        """Remplit automatiquement les lignes de commande du devis"""
        for wizard in self:
            if wizard.sale_id:
                wizard.order_line_ids = wizard.sale_id.order_line.filtered(
                    lambda l: l.product_id and l.state in ('draft', 'sent')
                )
            else:
                wizard.order_line_ids = [(5, 0, 0)]

    bom_line_ids = fields.Many2many(
        "mrp.bom.line",
        "sale_bom_wizard_m2m_bom_line_rel",
        "wizard_id", "bom_line_id",
        string="Composants sélectionnés",
        compute="_compute_bom_lines",
        store=False
    )

    # vendor_id = fields.Many2one(
    #     'res.partner',
    #     string="Fournisseur",
    #     required=True,
    #     domain=[('supplier_rank', '>', 0)],
    # )
    total_price = fields.Float(
        string="Prix Total des Composants",
        compute="_compute_total_price",
        readonly=True
    )

    @api.depends('order_line_ids')
    def _compute_bom_lines(self):
        """Récupère automatiquement les BoM lines de chaque produit sélectionné"""
        for wizard in self:
            all_bom_lines = []
            for line in wizard.order_line_ids:
                bom_dict = self.env['mrp.bom']._bom_find(line.product_id)
                # Boucle pour matcher la clé par ID pour éviter None
                bom = False
                for k, v in bom_dict.items():
                    if k.id == line.product_id.id:
                        bom = v
                        print('bom',bom)
                        break
                if bom:
                    all_bom_lines.extend(bom.bom_line_ids.ids)
            # Supprime les doublons
            wizard.bom_line_ids = [(6, 0, list(set(all_bom_lines)))]

    @api.depends('bom_line_ids.component_total')
    def _compute_total_price(self):
        for wizard in self:
            wizard.total_price = sum(wizard.bom_line_ids.mapped('component_total'))

    @api.model
    def default_get(self, fields_list):
        """ Pré-remplit avec la commande active """
        res = super().default_get(fields_list)
        ctx = self.env.context
        if ctx.get('active_model') == 'sale.order' and ctx.get('active_id'):
            sale = self.env['sale.order'].browse(ctx['active_id'])
            res['sale_id'] = sale.id
        return res

    def action_create_purchase_order(self):
        """ Crée un ou plusieurs bons de commande fournisseur selon le fournisseur des composants """
        self.ensure_one()

        if not self.bom_line_ids:
            return

        # Grouper par fournisseur
        bom_lines_by_supplier = {}
        for bl in self.bom_line_ids:
            if not bl.partner_id:
                raise UserError(
                    f"Le composant {bl.product_id.display_name} n’a pas de fournisseur défini."
                )
            bom_lines_by_supplier.setdefault(bl.partner_id.id, []).append(bl)

        for supplier_id, lines in bom_lines_by_supplier.items():
            po_lines = []
            for bl in lines:
                po_lines.append((0, 0, {
                    'product_id': bl.product_id.id,
                    'name': bl.product_id.display_name,
                    'product_qty': bl.product_qty or 1.0,
                    'product_uom': bl.product_uom_id.id,
                    'price_unit': bl.component_price,
                }))
            self.env['purchase.order'].create({
                'partner_id': supplier_id,
                'order_line': po_lines,
                'origin': self.sale_id.name or '',
            })

        return {'type': 'ir.actions.act_window_close'}


class SaleBomline(models.Model):
    _inherit = "mrp.bom.line"
    _description = "Sélection des composants à acheter"

    line_id = fields.Many2one('sale.bom.wizard', string="Wizard")

    component_price = fields.Float(
        string="Prix Unitaire",
        compute="_compute_component_price",
        readonly=True,
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Fournisseur",
        domain=[('supplier_rank', '>', 0)]
    )

    component_total = fields.Float(
        string="Prix Total",
        compute="_compute_component_total",
        readonly=True,
        store=True
    )

    @api.depends('product_id')
    def _compute_component_price(self):
        for line in self:
            line.component_price = line.product_id.lst_price if line.product_id else 0.0

    @api.depends('component_price', 'product_qty')
    def _compute_component_total(self):
        for line in self:
            line.component_total = line.product_qty * line.component_price



