from odoo import models, fields, api
from odoo.tools import amount_to_text_en

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    validate_by = fields.Many2one('res.users', string='Manager Approve')

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' ')
        convert_amount_in_words = convert_amount_in_words.replace('Rupiah')
        return convert_amount_in_words

class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    project_id = fields.Many2one('project.project', compute='compute_project_id')

    @api.one
    @api.depends('account_analytic_id')
    def compute_project_id(self):
        project_id = self.env['project.project'].search([('analytic_account_id', '=', self.account_analytic_id.id)],limit=1)
        self.project_id = project_id and project_id.id or False


    #@api.model
    #def create(self, vals):
    #    if vals.get('name', 'New') == 'New':
    #        vals['name'] = self.env['ir.sequence'].next_by_code('temp.value') or '/'
    #    return super(PurchaseOrder, self).create(vals)



