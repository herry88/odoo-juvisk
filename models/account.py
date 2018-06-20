from odoo import models, fields, api

class Journal(models.Model):
    _inherit = 'account.journal'

    sequence_out_id = fields.Many2one('ir.sequence', string='Entry Sequence Out',required=True, copy=False)

