# -*- coding: utf-8 -*-
{
    'name': "Prasetia Juvisk Sinergy",

    'summary': """
        Battery System Rent Module""",

    'description': """
        Odoo Juvisk yang ini
    """,

    'author': "easierware",
    'website': "http://www.easiere.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'project', 'sale', 'purchase','purchase_requisition', 'work_order'],

    # always loaded ,del company
    'data': [
        'report/purchase_report.xml',
        'report/purchase_request_report.xml',
        # 'report/invoice_report.xml',
        'report/stock_picking_report.xml',
        'report/account_move.xml',
        'report/account_payment.xml',
		'report/report_customer_invoice.xml',
        'report/report_deliveryslip.xml',
		'report/report_stock_picking.xml',
		'report/custom_css.xml',
        'report/report_so.xml',
        'report/reinburse_report.xml',
        #'report/picking_report_new.xml',
        'view/invoice.xml',
		'view/sale_view.xml',
        'view/account_view.xml',
		# 'wizard/account_report_general_ledger_view.xml',
		# 'report/report_generalledger_xls.xml',
        'data/juvisk_data.xml'
    ],
	#'css' : ['static/src/css/invoice_report.css'],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
