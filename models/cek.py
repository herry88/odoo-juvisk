from odoo import models, fields, api
from odoo.tools import amount_to_text_en
# from . import amount_to_text_en_id


class Invoice(models.Model):
    _inherit = 'account.invoice'
    sign_by = fields.Many2one('res.users', string='Sign by')
    sign_employee_id = fields.Many2one('hr.employee', compute='compute_employee_id')
    no_faktur = fields.Char(string='No Faktur')
    # po_id = fields.Char(sting='PO Reference', compute='_compute_partner_ref')
    deduction = fields.Monetary(string='Deduction', required=True)

    @api.one
    @api.depends('sign_by')
    def compute_employee_id(self):
       employee_id = self.env['hr.employee'].search([('user_id', '=', self.sign_by.id)],limit=1)
       self.sign_employee_id = employee_id and employee_id.id or False

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        convert_amount_in_words = convert_amount_in_words.replace('Rupiah', 'Rupiah ')
        return convert_amount_in_words

    # @api.one
    # @api.depends('purchase_id')
    # def _compute_partner_ref(self):
    #     # define obj purchase order
    #     # find purchase order based on name and stock picking origin
    #     # get requisition ID in purchase order save to self.partner_ref
    #
    #     print self.origin
    #     sale_order_data = self.env['sale.order'].search([('name','=',self.origin)])
    #
    #     for data in sale_order_data:
    #         self.po_id = data.client_order_ref
    #         #print data

        # purchase_id = self.env['purchase.order'].search([('purchase_id', '=', self.purchase_id.id)],limit=1)
        # self.purchase_id = purchase_id and purchase_id.id or False
#
# class LineInvoiceCustom(models.Model):
#     _inherit ='account.invoice.line'
#     deduction = fields.Monetary(string='Deduction')

