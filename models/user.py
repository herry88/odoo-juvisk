from odoo import models, fields, api

class Users(models.Model):
    _inherit = 'res.users'

    hand_signature = fields.Binary("Hand Signature", attachment=True,
        help="This field holds the image used as hand signature, limited to 1024x1024px",)
