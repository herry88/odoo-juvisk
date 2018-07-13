from odoo import models, fields, api
from odoo.tools import amount_to_text_en

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    #@api.model
    #def create(self, vals):
    #    if vals.get('name', 'New') == 'New':
    #        vals['name'] = self.env['ir.sequence'].next_by_code('temp.value') or '/'
    #    return super(PurchaseOrder, self).create(vals)

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' ')
        convert_amount_in_words = convert_amount_in_words.replace('Rupiah', 'Rupiah ')
        return convert_amount_in_words

