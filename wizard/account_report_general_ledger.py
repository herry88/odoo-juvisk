from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCommonReport(models.TransientModel):

    _inherit = "account.report.general.ledger"

    @api.multi
    def check_report_xls(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        # return self._print_report(data)

        return {'type': 'ir.actions.report.xml',
                'report_name': 'odoo-juvisk.report.generalledger.xlsx',
                'datas': data,
                'name': 'General Ledger Report'
                }
