from odoo import models, fields, api
from odoo.tools import amount_to_text_en


# from . import amount_to_text_en_id


class Invoice(models.Model):
    _inherit = 'account.invoice'

    sign_by = fields.Many2one('res.users', string='Sign by')
    sign_employee_id = fields.Many2one('hr.employee', compute='compute_employee_id')
    no_faktur = fields.Char(string='No Faktur')
    po_id = fields.Char(sting='PO Reference', compute='_compute_partner_ref')

    validate_by = fields.Many2one('res.users', string='Manager Approve')
    approve_by = fields.Many2one('res.users', string='Director Approve')
    # add state approve_director
    state = fields.Selection([
                ('draft','Draft'),
                ('proforma', 'Pro-forma'),
                ('proforma2', 'Pro-forma'),
                ('validate', 'Validated'),
                ('approve', 'Approved'),
                ('approve_director', 'Approved Director'),
                ('open', 'Open'),
                ('paid', 'Paid'),
                ('cancel', 'Cancelled'),
            ], string='Status', index=True, readonly=True, default='draft')


    @api.multi
    def invoice_validate(self):
        for invoice in self:
            # refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/refund
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                vstate = 'approve'
                if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference),
                                ('company_id', '=', invoice.company_id.id),
                                ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
                                ('id', '!=', invoice.id)]):
                    raise UserError(_(
                        "Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
            else :
                vstate = 'open'

        return self.write({'state': vstate})

    @api.multi
    def action_invoice_approve(self):
        self.write({'state': 'approve_director', 'validate_by': self.env.uid})

    @api.multi
    def action_invoice_approve_director(self):
        self.write({'state': 'open', 'approve_by': self.env.uid})

    # deduction = fields.Monetary(string='Deduction')

    @api.one
    @api.depends('sign_by')
    def compute_employee_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.sign_by.id)], limit=1)
        self.sign_employee_id = employee_id and employee_id.id or False

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero', ' ')
        convert_amount_in_words = convert_amount_in_words.replace(',', ' ')
        convert_amount_in_words = convert_amount_in_words + ' Rupiah'
        return convert_amount_in_words

    @api.one
    @api.depends('purchase_id')
    def _compute_partner_ref(self):
        # define obj purchase order
        # find purchase order based on name and stock picking origin
        # get requisition ID in purchase order save to self.partner_ref

        print self.origin
        sale_order_data = self.env['sale.order'].search([('name', '=', self.origin)])

        for data in sale_order_data:
            self.po_id = data.client_order_ref
            # print data

        # purchase_id = self.env['purchase.order'].search([('purchase_id', '=', self.purchase_id.id)],limit=1)
        # self.purchase_id = purchase_id and purchase_id.id or False

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0) - line.deduction
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': self.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
                    'account_id': self.type in ('out_invoice', 'in_invoice') and (
                                tax['account_id'] or line.account_id.id) or (
                                              tax['refund_account_id'] or line.account_id.id),
                }
                if not val.get('account_analytic_id') and line.account_analytic_id and val[
                    'account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id
                key = tax['id']
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
        return tax_grouped


class LineInvoiceCustom(models.Model):
    _inherit = 'account.invoice.line'
    deduction = fields.Monetary(string='Deduction')

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0) - self.deduction
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
