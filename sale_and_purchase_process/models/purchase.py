from odoo import api, fields, models
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    interco_status = fields.Selection([
        ("draft","Brouillon"),
        ("to_validate","À valider"),
        ("sent_partner","Envoyé partenaire"),
        ("ack_partner","Accusé de réception"),
        ("in_progress","En cours"),
        ("shipped","Expédié"),
        ("received","Reçu"),
        ("invoiced","Facturé"),
        ("paid","Payé"),
        ("blocked","Bloqué"),
        ("cancel","Annulé"),
    ], default="draft", string="Statut Interco", tracking=True)

    interco_counterpart_model = fields.Selection([("sale.order","SO"),("purchase.order","PO")], copy=False)
    interco_counterpart_id = fields.Integer(copy=False)

    def button_confirm(self):
        res = super().button_confirm()
        for po in self:
            if self.env.context.get("skip_interco"):
                continue
            if not po.interco_counterpart_id:
                so, link = self.env["interco.link"]._make_so_from_po(po)
                po.message_post(body=f"SO interco créé: <b>{so.name}</b> ({so.company_id.name})")
        return res

    def action_set_interco_status(self, status):
        allowed = dict(self._fields['interco_status'].selection).keys()
        if status not in allowed:
            raise UserError("Statut non supporté")
        for po in self:
            po.write({"interco_status": status})
            link = self.env["interco.link"].search([
                ("origin_model","=","purchase.order"), ("origin_id","=",po.id)
            ], limit=1) or self.env["interco.link"].search([
                ("counterpart_model","=","purchase.order"), ("counterpart_id","=",po.id)
            ], limit=1)
            if link:
                link.sync_status(status)