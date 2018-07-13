from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en

# import amount_to_text_id


class Reimbursement(models.Model):
    _inherit = "account.voucher"

    # @api.one
    # @api.depends('amount')
    # def _amount_in_words(self):
    #     # self.amount_to_text = amount_to_text_id(self.amount_total, self.currency_id.symbol)
    #     self.amount_to_text = amount_to_text_id.amount_to_text_id_call(self.amount)

    @api.model
    def _default_journal(self):
        voucher_type = self._context.get('voucher_type', 'bank')
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', voucher_type),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    amount_to_text = fields.Text(string='In Words',
                                 store=True, readonly=True, compute='_amount_in_words')
    type_transaction = fields.Selection([
        ('reimburse', 'Reimburse'),
    ], readonly=True, index=True, change_default=True,
        default=lambda self: self._context.get('type_transaction', 'voucher'),
        track_visibility='always')
    # state = fields.Selection(selection_add=[('confirm', 'Confirmed'),('validate', 'Validate')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Wait Approval Manager'),
        ('validate', 'Wait Payment'),
        ('cancel', 'Cancelled'),
        ('proforma', 'Pro-forma'),
        ('posted', 'Paid')
    ], 'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.")
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 required=True, readonly=True, states={'validate': [('readonly', False)]},
                                 default=_default_journal)

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        self.account_id = self.journal_id.default_debit_account_id

    @api.multi
    def confirm_voucher(self):
        for reimb in self:
            if reimb.number:
                number = reimb.number
            else:
                number = self.env['ir.sequence'].next_by_code('voucher.reimburse')
        self.write({'state': 'confirm', 'number': number})

    @api.multi
    def validate_voucher(self):
        self.write({'state': 'validate'})

    def account_move_get(self):
        if self.journal_id.sequence_id:
            if not self.journal_id.sequence_id.active:
                raise UserError(_('Please activate the sequence of selected journal !'))
            name = self.journal_id.sequence_id.with_context(ir_sequence_date=self.date).next_by_id()
        else:
            raise UserError(_('Please define a sequence on the journal.'))

        move = {
            'name': name,
            'journal_id': self.journal_id.id,
            'narration': self.narration,
            'date': self.account_date,
            'ref': self.number,
        }
        return move

    @api.multi
    def action_move_line_create(self):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        for voucher in self:
            local_context = dict(self._context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = voucher.journal_id.company_id.currency_id.id
            current_currency = voucher.currency_id.id or company_currency
            # we select the context to use accordingly if it's a multicurrency case or not
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = local_context.copy()
            ctx['date'] = voucher.account_date
            ctx['check_move_validity'] = False
            # Create the account move record.
            move = self.env['account.move'].create(voucher.account_move_get())
            # Get the name of the account_move just created
            # Create the first line of the voucher
            move_line = self.env['account.move.line'].with_context(ctx).create(
                voucher.with_context(ctx).first_move_line_get(move.id, company_currency, current_currency))
            line_total = move_line.debit - move_line.credit
            if voucher.voucher_type == 'sale':
                line_total = line_total - voucher._convert_amount(voucher.tax_amount)
            elif voucher.voucher_type == 'purchase':
                line_total = line_total + voucher._convert_amount(voucher.tax_amount)
            # Create one move line per voucher line where amount is not 0.0
            line_total = voucher.with_context(ctx).voucher_move_line_create(line_total, move.id, company_currency,
                                                                            current_currency)

            # Add tax correction to move line if any tax correction specified
            if voucher.tax_correction != 0.0:
                tax_move_line = self.env['account.move.line'].search(
                    [('move_id', '=', move.id), ('tax_line_id', '!=', False)], limit=1)
                if len(tax_move_line):
                    tax_move_line.write(
                        {'debit': tax_move_line.debit + voucher.tax_correction if tax_move_line.debit > 0 else 0,
                         'credit': tax_move_line.credit + voucher.tax_correction if tax_move_line.credit > 0 else 0})

            # We post the voucher.
            voucher.write({
                'move_id': move.id,
                'state': 'posted'
            })
            move.post()
        return True
