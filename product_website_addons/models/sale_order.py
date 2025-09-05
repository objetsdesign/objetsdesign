from odoo import fields, models, api


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    # Champs pour tes informations
    tech_doc = fields.Text(string="Document Technique",
                           default="A fournir document sous illustrator avec couleur pantone")
    delivery_info = fields.Text(string="Livraison",
                                default="Franco 1 point France métropolitaine à partir de 1 000 € HT sans option")
    payment_info = fields.Text(string="Règlement", default="30 jours fin de mois date de facture")
    validity_info = fields.Text(string="Validité", default="Offre valide deux semaines")
    delay_info = fields.Text(string="Délai", default="Indiqué sur le devis et ne comprends pas les cas de force majeur")
    inspection_info = fields.Text(string="Inspections",
                                  default="Nos inspections respectent l'AQL des normes international ANSI/ASQ Z1.4-2003 / ISO 2859/1")
    address_china = fields.Char(string="Adresse Chine",
                                default="313 to 315, Block C, Hong Wan business center Gushu, Bao’an Area, Shenzhen, China")
    address_tunisia = fields.Char(string="Adresse Tunisie",
                                  default="Boulevard 14 Janvier Immeuble Elbahri 4011 Hammam Sousse")
    total_frais_technique = fields.Float(
        string="Total Frais Technique", compute="_compute_total_frais_technique", store=True
    )

    @api.depends("order_line.product_id.x_frais_tech")
    def _compute_total_frais_technique(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                if line.product_id.x_frais_tech:
                    total += line.product_id.x_frais_tech
            order.total_frais_technique = total


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    delai_bat = fields.Char(string="Délai Bat", compute='_compute_stock_info', store=True)
    delai_livraison = fields.Char(string="Délai de livraison", compute='_compute_stock_info', store=True)
    print_in_quote = fields.Boolean(string="Imprimer ce produit sur le devis")

    @api.depends('order_id.picking_ids')  # dépend du picking de la commande
    def _compute_stock_info(self):
        for line in self:
            picking = line.order_id.picking_ids[:1]  # premier picking lié à la commande
            if picking:
                line.delai_bat = picking.scheduled_date or ''
                line.delai_livraison = picking.date_done or ''
            else:
                line.delai_bat = ''
                line.delai_livraison = ''


class ProductProduct(models.Model):
    _inherit = "product.template"
    x_matiere = fields.Char(string="Matière")
    x_dimensions = fields.Char(string="Dimensions")
    x_marquage = fields.Char(string="Marquage")
    x_conditionnement = fields.Char(string="Conditionnement")
    x_etiquette = fields.Char(string="Etiquette")
    x_infos = fields.Text(string="Infos supplémentaires")
    x_frais_tech = fields.Float(string="Frais Technique")
