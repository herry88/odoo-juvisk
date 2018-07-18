from odoo import models, fields, api

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    validate_by = fields.Many2one('res.users', string='Manager Approve')

    @api.multi
    def action_open(self):
        self.write({'state': 'open','validate_by':self.env.uid})
