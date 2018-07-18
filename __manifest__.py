# -*- coding: utf-8 -*-
{
    'name': "Prasetia Juvisk Sinergy",

    'summary': """
        Battery System Rent Module""",

    'description': """
        Battery System Rent Module
    """,

    'author': "easierware",
    'website': "http://www.easiere.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'project', 'sale', 'purchase','purchase_requisition', 'work_order','hr_maintenance'],

    # always loaded ,del company
    'data': [
        'report/purchase_report.xml',
        'report/purchase_request_report.xml',
        'report/stock_picking_report.xml',
        'report/account_move.xml',
        'report/account_payment.xml',
		'report/report_customer_invoice.xml',
        'report/report_deliveryslip.xml',
		'report/report_stock_picking.xml',
		'report/custom_css.xml',
		'report/invoice_report.xml',
        'report/report_so.xml',
		'report/vendor_bills_report.xml',
        'report/reinburse_report.xml',
        'view/invoice.xml',
        'view/budget.xml',
        'view/purchase_request.xml',
        'view/site.xml',
		'view/sale_view.xml',
        'view/project_view.xml',
        'view/account_view.xml',
		'view/batteryrent_view.xml',
		'view/equipment_view.xml',
		'view/reimburse_views.xml',
        'data/project_data.xml',
		'data/reimburse_data.xml',
        'data/juvisk_data.xml',
		'data/equipment_data.xml'
    ],
	#'css' : ['static/src/css/invoice_report.css'],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
