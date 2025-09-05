from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ProductsTemplate(models.Model):
    _inherit = 'product.template'

    website_description = fields.Html('Website Description', translate=True)
    short_description = fields.Char('Short Description', translate=True)

    custom_description = fields.Html("Custom Description", translate=True)

