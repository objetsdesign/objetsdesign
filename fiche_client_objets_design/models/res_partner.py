from odoo import models, fields, api

class PartnerBudgetFournisseur(models.Model):
    _name = "partner.budget.fournisseur"
    _description = "Budget Partner Fournisseur"
    name = fields.Char(string="Nom", required=True)  # Haute, Moyenne, Faible

    color_class = fields.Selection([
        ("haute", "Haute"),
        ("moyenne", "Moyenne"),
        ("faible", "Faible"),
    ], string="Classe", required=True)
    color = fields.Integer(
        string="Couleur",
        compute="_compute_color",
        store=True
    )

    @api.depends("color_class")
    def _compute_color(self):
        """Assigne un index de couleur (0–11) selon color_class"""
        mapping_fournisseur = {
            "haute": 0,
            "moyenne": 1,
            "faible": 2,
        }
        for rec in self:
            rec.color = mapping_fournisseur.get(rec.color_class, 0)

class PartnerBudget(models.Model):
    _name = "partner.budget"
    _description = "Budget Partner"

    name = fields.Char(string="Nom", required=True)  # Bronze, Silver, Gold

    color_class = fields.Selection([
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
    ], string="Classe", required=True)


    # Champ obligatoire pour many2many_tags
    color = fields.Integer(
        string="Couleur",
        compute="_compute_color",
        store=True
    )

    @api.depends("color_class")
    def _compute_color(self):
        """Assigne un index de couleur (0–11) selon color_class"""
        mapping = {
            "bronze": 0,  # Marron
            "silver": 1,  # Gris
            "gold": 2,  # Jaune
        }
        for rec in self:
            rec.color = mapping.get(rec.color_class, 0)


class RespartnerInherit(models.Model):
    _inherit = "res.partner"
    _description = "Liste des clients"

    secteur_activite = fields.Char(string="Secteur d’activité")
    nbr_site = fields.Char(string="Nombre de sites / sièges")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # --- Équipe interne ---
    commercial_id = fields.Many2one('res.users', string="Commercial assigné")
    autres_commerciaux_ids = fields.Many2many(
        'res.users', 'res_partner_commerciaux_rel', 'partner_id', 'user_id',
        string="Autres commerciaux liés"
    )
    responsable_projet_id = fields.Many2one('res.users', string="Responsable projet / ADV")
    referent_logistique_id = fields.Many2one('res.users', string="Référent logistique")
    referent_facturation_id = fields.Many2one('res.users', string="Référent facturation")

    budget_ids = fields.Many2many(
        "partner.budget",
        string="Importance"
    )
    zone = fields.Selection([
        ('dp_france', 'DP-France'),
        ('dp_allemagne', 'DP-Allemagne'),
        ('dp_tunisie', 'DP-Tunisie'),
        ('dp_autre', 'Autre'),
    ], string="Zone")

    produits = fields.Selection([
        ('textile', 'Textile'),
        ('maroquinerie', 'Maroquinerie'),
        ('electronique', 'Électronique'),
        ('ceramique', 'Céramique'),
    ], string="Produits")
    gold_vip_text = fields.Char(
        string="VIP Badge",
        compute="_compute_gold_vip_text",
        store=True
    )
    prenom = fields.Char(string="Prénom")
    site_location = fields.Char(string="Localisation / Site")
    influence = fields.Selection([
        ('d', 'Décideur'),
        ('a', 'Approuveur'),
        ('c', 'Consulté'),
        ('i', 'Informé'),
    ], string="Influence (D/A/C/I)")
    observation = fields.Text(string="Observations")
    @api.depends('gold_vip')
    def _compute_gold_vip_text(self):
        for partner in self:
            partner.gold_vip_text = "Gold VIP" if partner.gold_vip else ""
    # --- Classification client ---
    statut_relationnel = fields.Selection([
        ("prospect_froid", "Prospect froid"),
        ("prospect_chaud", "Prospect chaud"),
        ("actif", "Client actif"),
        ("inactif", "Client inactif"),
    ], string="Statut relationnel")

    potentiel_strategique = fields.Selection([
        ("vip", "VIP"),
        ("strategique", "Stratégique"),
        ("one_shot", "One shot"),
    ], string="Potentiel stratégique")

    type_client = fields.Selection([
        ("agence", "Agence"),
        ("b2b", "B2B direct"),
        ("marketplace", "Marketplace"),
        ("particulier", "Particulier"),
    ], string="Type client")

    pays_zone = fields.Many2one("res.country", string="Pays")
    region_zone = fields.Char(string="Région")
    is_client = fields.Boolean(string="Client", compute='_compute_is_client', store=True)

    # --- Historique & suivi ---
    company_currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True
    )

    ca_cumule = fields.Monetary(string="CA cumulé", compute="_compute_stats")
    commandes_nb = fields.Integer(string="Nombre de commandes", compute="_compute_stats")
    commandes_montant = fields.Monetary(
        string="Montant des commandes", compute="_compute_stats",
        currency_field='company_currency_id'
    )
    produits_achetes = fields.Char(
        string="Produits achetés / demandés", compute="_compute_produits_achetes"
    )

    derniere_interaction_date = fields.Datetime(
        string="Dernière interaction (date)", compute="_compute_interactions"
    )
    derniere_interaction_type = fields.Char(
        string="Type interaction", compute="_compute_interactions"
    )

    prochaine_action_date = fields.Datetime(string="Prochaine action prévue")
    prochaine_action_responsable_id = fields.Many2one('res.users', string="Responsable")
    prochaine_action_type = fields.Selection([
        ('appel', 'Appel'),
        ('visite', 'Visite'),
        ('mail', 'Mail'),
        ('devis', 'Devis'),
    ], string="Type action")
    discount_conditions = fields.Float(
        string="Remise négociée (%)",
        compute="_compute_discount_conditions",
        store=True
    )
    satisfaction_score = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)],
        string="Score de satisfaction"
    )
    feedbacks = fields.Text(string="Feedbacks récents")
    improvement_points = fields.Text(string="Points d'amélioration / Risques identifiés")
    last_followup_date = fields.Date(
        string="Dernière relance",
        compute="_compute_last_followup_date",
        store=True
    )

    @api.depends('activity_ids.date_deadline')
    def _compute_last_followup_date(self):
        for partner in self:
            dates = partner.activity_ids.mapped('date_deadline')
            partner.last_followup_date = max(dates) if dates else False
    @api.depends('invoice_ids.invoice_line_ids.discount')
    def _compute_discount_conditions(self):
        for partner in self:
            discounts = partner.invoice_ids.mapped('invoice_line_ids.discount')
            if discounts:
                # Par exemple on prend la moyenne des remises
                partner.discount_conditions = sum(discounts) / len(discounts)
            else:
                partner.discount_conditions = 0.0

    payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Délais de paiement",
        compute="_compute_payment_terms_id",
        store=True,
    )

    @api.depends("sale_order_ids.payment_term_id")
    def _compute_payment_terms_id(self):
        for partner in self:
            if partner.sale_order_ids:
                # On prend le dernier SO validé avec un délai de paiement
                last_so = partner.sale_order_ids.filtered(
                    lambda so: so.payment_term_id
                ).sorted("date_order", reverse=True)[:1]
                partner.payment_term_id = last_so.payment_term_id if last_so else False
            else:
                partner.payment_term_id = False

    # Champ pour le paiement lié aux commandes d'achat
    purchase_payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Délais de paiement fournisseur",
        compute="_compute_purchase_payment_terms_id",
        store=True,
    )

    @api.depends("purchase_order_ids.payment_term_id")
    def _compute_purchase_payment_terms_id(self):
        for partner in self:
            if partner.purchase_order_ids:
                # On prend le dernier PO validé avec un délai de paiement
                last_po = partner.purchase_order_ids.filtered(
                    lambda po: po.payment_term_id
                ).sorted("date_order", reverse=True)[:1]
                partner.purchase_payment_term_id = last_po.payment_term_id if last_po else False
            else:
                partner.purchase_payment_term_id = False

    incoterm_id = fields.Many2one(
        "account.incoterms",
        string="Incoterm",
        compute="_compute_incoterm_id",
        store=True,
    )
    special_conditions = fields.Boolean(string="Conditions particulières")
    gold_vip = fields.Boolean(string="Gold VIP")
    certification_ids = fields.Many2many(
        'partner.certification',  # modèle à créer pour les certifications
        string="Certifications"
    )

    quality_incident_ids = fields.One2many(
        'partner.quality.incident',  # modèle à créer pour incidents qualité
        'partner_id',
        string="Historique incidents qualité"
    )

    @api.depends("invoice_ids.invoice_incoterm_id")
    def _compute_incoterm_id(self):
        for partner in self:
            if partner.invoice_ids:
                # On prend la dernière facture validée avec un incoterm défini
                last_invoice = partner.invoice_ids.filtered(
                    lambda inv: inv.invoice_incoterm_id
                ).sorted("invoice_date", reverse=True)[:1]
                partner.incoterm_id = last_invoice.invoice_incoterm_id if last_invoice else False
            else:
                partner.incoterm_id = False


    contract_particularities = fields.Char(string="Particularités contractuelles")
    in_company_1 = fields.Boolean(compute="_compute_in_company_1", store=False)

    def _compute_in_company_1(self):
        current_company_id = self.env.company.id
        for rec in self:
            rec.in_company_1 = (current_company_id == 1)   # cache si la société courante a l’ID 1

    # --------------------
    # COMPUTES
    # --------------------

    @api.depends('customer_rank')
    def _compute_is_client(self):
        for partner in self:
            partner.is_client = partner.customer_rank > 0

    @api.depends('sale_order_ids.amount_total', 'sale_order_ids.state')
    def _compute_stats(self):
        for partner in self:
            orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            partner.ca_cumule = sum(orders.mapped('amount_total'))
            partner.commandes_nb = len(orders)
            partner.commandes_montant = sum(orders.mapped('amount_total'))

    @api.depends('sale_order_ids.order_line.product_id')
    def _compute_produits_achetes(self):
        for partner in self:
            products = partner.sale_order_ids.order_line.mapped('product_id.name')
            partner.produits_achetes = ", ".join(set(products)) if products else False

    @api.depends('message_ids.date')
    def _compute_interactions(self):
        """ Exemple : basé sur le chatter (mail.message) """
        for partner in self:
            last_message = partner.message_ids.sorted('date', reverse=True)[:1]
            if last_message:
                partner.derniere_interaction_date = last_message.date
                partner.derniere_interaction_type = last_message.subtype_id.name or "Note"
            else:
                partner.derniere_interaction_date = False
                partner.derniere_interaction_type = False
# Fournisseur
    purchase_responsible_id = fields.Many2one(
        "res.users", string="Responsable Achat"
    )
    other_buyers_ids = fields.Many2many(
        "res.users", string="Autres Acheteurs"
    )
    quality_ref_id = fields.Many2one(
        "res.users", string="Référent Qualité"
    )
    logistic_ref_id = fields.Many2one(
        "res.users", string="Référent Logistique"
    )
    billing_ref_id = fields.Many2one(
        "res.users", string="Référent Facturation")
    supplier_fiability = fields.Many2many(
        "partner.budget.fournisseur",
        string="Fiabilité"
    )
    supplier_dependence = fields.Selection([
        ('strategic', 'Stratégique'),
        ('secondary', 'Secondaire'),
        ('alternative', 'Alternatif'),
    ], string="Niveau de dépendance")

    supplier_type = fields.Selection([
        ('subcontractor', 'Sous-traitant'),
        ('raw_material', 'Matière première'),
        ('key_partner', 'Partenaire clé'),
    ], string="Type de fournisseur")

    supplier_zone = fields.Char(string="Zone géographique")
    volume_achats_cumule = fields.Monetary(
        string="Volume d’achats cumulé",
        currency_field="currency_id",
        compute="_compute_historique_suivi",
        store=False
    )
    commandes_passees_count = fields.Integer(
        string="Nombre de commandes passées",
        compute="_compute_historique_suivi",
        store=False
    )
    commandes_passees_montant = fields.Monetary(
        string="Montant commandes passées",
        currency_field="currency_id",
        compute="_compute_historique_suivi",
        store=False
    )
    produits_fournis_ids = fields.Many2many(
        "product.product",
        string="Produits / matières fournis",
        compute="_compute_historique_suivi",
        store=False,
        readonly=True
    )

    derniere_interaction = fields.Char(string="Dernière interaction (texte)")

    prochaine_action = fields.Char(
        string="Prochaine action prévue",
        # compute="_compute_interactions",
        store=False
    )
    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="partner_id",
        string="Commandes fournisseur"
    )
    derniere_interaction_date = fields.Datetime(
        string="Dernière interaction (date)",
        compute="_compute_historique_suivi",
        store=True
    )

    @api.depends("purchase_order_ids", "purchase_order_ids.order_line")
    def _compute_historique_suivi(self):
        for partner in self:
            orders = self.env["purchase.order"].search([("partner_id", "=", partner.id), ("state", "in", ["purchase", "done"])])
            partner.commandes_passees_count = len(orders)
            partner.commandes_passees_montant = sum(orders.mapped("amount_total"))
            partner.volume_achats_cumule = partner.commandes_passees_montant
            partner.produits_fournis_ids = orders.mapped("order_line.product_id")

    class PartnerCertification(models.Model):
        _name = 'partner.certification'
        _description = 'Certification Partner'

        name = fields.Char(string='Nom', required=True)  # ISO, CE, autre
        description = fields.Text(string='Description')

    class PartnerQualityIncident(models.Model):
        _name = 'partner.quality.incident'
        _description = 'Quality Incident'

        partner_id = fields.Many2one('res.partner', string='Fournisseur', required=True)
        date_incident = fields.Date(string='Date de l’incident', required=True)
        description = fields.Text(string='Description')







