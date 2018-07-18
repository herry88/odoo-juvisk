from odoo import models, fields, api

class Company(models.Model):
    _inherit = "res.company"

    code = fields.Char(string="Sequence Code")
