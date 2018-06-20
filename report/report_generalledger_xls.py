from datetime import datetime

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class report_generalledger_xls(ReportXlsx):
    format_prasetia_bold = None
    format_prasetia_header = None
    format_prasetia_header_table_center = None
    format_prasetia_data_table_normal = None
    format_prasetia_data_table_header = None
    format_prasetia_data_table_header_number = None
    format_prasetia_data_table_date = None
    format_prasetia_data_table_number = None

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(
                date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    def generate_xlsx_report(self, workbook, data, lines):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        # display_account = data['form']['display_account']
        display_account = data['form'].get('display_account', 'movement')
        target_move = data['form'].get('target_move', 'posted')

        # set format style xls
        self.format_prasetia_bold = workbook.add_format({'bold': True})
        self.format_prasetia_header_table_center = workbook.add_format({'bold': True,
                                                                        'align': 'center'
                                                                        })
        self.format_prasetia_data_table_normal = workbook.add_format({'align': 'left',
                                                                      'font_size': 12})
        self.format_prasetia_data_table_header = workbook.add_format({'bold': True,
                                                                      'align': 'left',
                                                                      'font_size': 12})
        self.format_prasetia_data_table_header_number = workbook.add_format({'bold': True,
                                                                      'align': 'left',
                                                                      'font_size': 12,
                                                                      'num_format': '#,##0.00'})
        self.format_prasetia_data_table_number = workbook.add_format({'align': 'left',
                                                                      'font_size': 12,
                                                                      'num_format': '#,##0.00'})
        self.format_prasetia_data_table_date = workbook.add_format({'align': 'left',
                                                                    'font_size': 12,
                                                                    'num_format': 'd mmmm yyyy'})
        self.format_prasetia_header = workbook.add_format({'bold': True,
                                                           'font_size': 22,
                                                           'align': 'center'})

        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]

        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        # accounts_res = self.with_context(data['form'].get('used_context', {}))._get_account_move_entry(accounts,
        #                                                                                                init_balance,
        #                                                                                                sortby,
        #                                                                                                display_account)
        accounts_res = self._get_account_move_entry(accounts, init_balance, sortby, display_account)

        sheet = workbook.add_worksheet('General Ledger')
        sheet.merge_range('A1:I1', 'PT Prasetia Juvisk Sinergi: General Ledger', self.format_prasetia_header)

        journal = ','.join(str(code) for code in codes)

        # format colums
        sheet.set_column('A:A', 17, self.format_prasetia_header_table_center)
        sheet.set_column('B:B', 5, self.format_prasetia_header_table_center)
        sheet.set_column('C:C', 20, self.format_prasetia_header_table_center)
        sheet.set_column('D:D', 15, self.format_prasetia_header_table_center)
        sheet.set_column('E:E', 15, self.format_prasetia_header_table_center)
        sheet.set_column('F:F', 18, self.format_prasetia_header_table_center)
        sheet.set_column('G:G', 18, self.format_prasetia_header_table_center)
        sheet.set_column('H:H', 18, self.format_prasetia_header_table_center)
        sheet.set_column('I:I', 18, self.format_prasetia_header_table_center)
        # End Format Columns

        sheet.write("A3", 'Jurnals', self.format_prasetia_bold)
        sheet.write("A4", journal, self.format_prasetia_data_table_normal)
        sheet.merge_range("E3:G3", 'Display Acounts', self.format_prasetia_bold)
        sheet.merge_range("E4:G4", display_account, self.format_prasetia_data_table_normal)
        sheet.write("I3", 'Target Moves:', self.format_prasetia_bold)
        sheet.write("I4", target_move, self.format_prasetia_data_table_normal)
        sheet.merge_range("A6:B6", 'Sorted By:', self.format_prasetia_bold)
        sheet.merge_range("A7:B7", sortby, self.format_prasetia_data_table_normal)

        sheet.write("A9", 'Date', self.format_prasetia_header_table_center)
        sheet.write("B9", 'JRNL', self.format_prasetia_header_table_center)
        sheet.write("C9", 'Partner', self.format_prasetia_header_table_center)
        sheet.write("D9", 'Ref', self.format_prasetia_header_table_center)
        sheet.write("E9", 'Move', self.format_prasetia_header_table_center)
        sheet.write("F9", 'Entry Label', self.format_prasetia_header_table_center)
        sheet.write("G9", 'Debit', self.format_prasetia_header_table_center)
        sheet.write("H9", 'Credit', self.format_prasetia_header_table_center)
        sheet.write("I9", 'Balance', self.format_prasetia_header_table_center)

        num_rows = 10
        for data in accounts_res:
            sheet.write("A{0}".format(num_rows), data['code'], self.format_prasetia_data_table_header)
            sheet.merge_range("B{0}:F{0}".format(num_rows), data['name'], self.format_prasetia_data_table_header)
            sheet.write("G{0}".format(num_rows), data['debit'], self.format_prasetia_data_table_header_number)
            sheet.write("H{0}".format(num_rows), data['credit'], self.format_prasetia_data_table_header_number)
            sheet.write("I{0}".format(num_rows), data['balance'], self.format_prasetia_data_table_header_number)
            num_rows+=1

            for line in data['move_lines']:
                sheet.write("A{0}".format(num_rows), line['ldate'], self.format_prasetia_data_table_date)
                sheet.write("B{0}".format(num_rows), line['lcode'], self.format_prasetia_data_table_normal)
                sheet.write("C{0}".format(num_rows), line['partner_name'], self.format_prasetia_data_table_normal)
                sheet.write("D{0}".format(num_rows), line['lref'] if line['lref'] else '', self.format_prasetia_data_table_normal)
                sheet.write("E{0}".format(num_rows), line['move_name'], self.format_prasetia_data_table_normal)
                sheet.write("F{0}".format(num_rows), line['lname'], self.format_prasetia_data_table_normal)
                sheet.write("G{0}".format(num_rows), line['debit'], self.format_prasetia_data_table_number)
                sheet.write("H{0}".format(num_rows), line['credit'], self.format_prasetia_data_table_number)
                sheet.write("I{0}".format(num_rows), line['balance'], self.format_prasetia_data_table_number)
                num_rows+=1



report_generalledger_xls('report.odoo-juvisk.report.generalledger.xlsx', 'account.journal')
