from abc import ABC

from odoo import models, fields, api, exceptions, _
from datetime import date, timedelta

from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    kanban_status = fields.Selection([
        ("green", "Actif"),
        ("red", "Inactif"),
    ], string="Statut Kanban", compute="_compute_kanban_status", store=False)
    is_commercial = fields.Boolean(string="Est un commercial ?", default=False)
    commercial_ids = fields.One2many(
        "partner.commercial",
        "partner_id",
        string="Commerciaux",
        compute="_compute_commercial_ids",
        store=True
    )

    def create(self, vals_list):
        # Odoo peut envoyer un seul dict ou une liste de dicts
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            # Vérifie si l'email existe déjà
            if vals.get("email"):
                existing_email = self.search([("email", "=", vals["email"])], limit=1)
                if existing_email:
                    raise ValidationError(
                        _("Un partenaire avec le même email existe déjà : %s <%s>") %
                        (existing_email.name, existing_email.email)
                    )

            # Vérifie si le nom existe déjà
            if vals.get("name"):
                existing_name = self.search([("name", "=", vals["name"])], limit=1)
                if existing_name:
                    raise ValidationError(
                        _("Un partenaire avec le même nom existe déjà : %s") %
                        existing_name.name
                    )

        return super(ResPartnerInherit, self).create(vals_list)


    def write(self, vals):
        for partner in self:
            # Vérifie email
            if vals.get("email"):
                existing_email = self.search([
                    ("email", "=", vals["email"]),
                    ("id", "!=", partner.id)
                ], limit=1)
                if existing_email:
                    raise ValidationError(
                        _("Un partenaire avec le même email existe déjà : %s <%s>") %
                        (existing_email.name, existing_email.email)
                    )

            # Vérifie nom
            if vals.get("name"):
                existing_name = self.search([
                    ("name", "=", vals["name"]),
                    ("id", "!=", partner.id)
                ], limit=1)
                if existing_name:
                    raise ValidationError(
                        _("Un partenaire avec le même nom existe déjà : %s") %
                        existing_name.name
                    )
        return super(ResPartnerInherit, self).write(vals)

    @api.depends("child_ids", "child_ids.is_commercial")
    def _compute_commercial_ids(self):
        for partner in self:
            commercial_lines = []
            for child in partner.child_ids:
                if child.is_commercial:
                    commercial_lines.append((0, 0, {'contact_id': child.id}))
            partner.commercial_ids = [(5, 0, 0)] + commercial_lines

    @api.onchange('child_ids')
    def _onchange_child_commercials(self):
        for partner in self:
            commercial_lines = []
            for child in partner.child_ids:
                if child.is_commercial:
                    if not partner.commercial_ids.filtered(lambda c: c.contact_id == child):
                        commercial_lines.append((0, 0, {'contact_id': child.id}))
            partner.commercial_ids = [(5, 0, 0)] + commercial_lines

            # Debug propre
            _logger.info("commercial_ids mis à jour pour %s : %s",
                         partner.name, partner.commercial_ids.ids)

    # @api.onchange('child_ids')
    # def _onchange_child_commercials(self):
    #     for partner in self:
    #         commercial_lines = []
    #         for child in partner.child_ids:
    #             if getattr(child, 'is_commercial', False):
    #                 # Si le contact n'existe pas déjà dans le One2many
    #                 existing = partner.commercial_ids.filtered(lambda c: c.contact_id == child)
    #                 print('existing',existing)
    #                 if not existing:
    #                     test=commercial_lines.append((0, 0, {
    #                         'contact_id': child.id,
    #                     }))
    #                     print('commercial_lines', commercial_lines)
    #
    #         # Remplace tout le One2many par la nouvelle liste
    #         partner.commercial_ids = [(5, 0, 0)] + commercial_lines

    @api.depends("sale_order_ids.partner_id", "sale_order_ids.validity_date")
    def _compute_kanban_status(self):
        one_year_ago = fields.Date.today() - timedelta(days=365)
        for partner in self:
            orders = partner.sale_order_ids
            if not orders:
                partner.kanban_status = "green"
            else:
                valid_orders = orders.filtered(
                    lambda o: o.validity_date and o.validity_date >= one_year_ago
                )
                partner.kanban_status = "green" if valid_orders else "red"


class PartnerCommercial(models.Model):
    _name = "partner.commercial"
    _description = "Commercial lié à un partenaire"

    partner_id = fields.Many2one("res.partner", string="Parent", ondelete="cascade")
    contact_id = fields.Many2one("res.partner", string="Contact")
    contact_name = fields.Char(related="contact_id.name", store=True)
    function = fields.Char(related="contact_id.function", store=True)
    phone = fields.Char(related="contact_id.phone", store=True)
    email = fields.Char(related="contact_id.email", store=True)
    is_commercial = fields.Boolean(
        string="Est un commercial ?",
        related="contact_id.is_commercial",
        store=True
    )
