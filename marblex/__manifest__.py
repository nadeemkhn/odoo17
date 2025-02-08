# -*- coding: utf-8 -*-
{
    'name': "Marblex",
    'summary': "This module customizes the sale process.",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Sales',
    'version': '17.0.1.0',
    'depends': [
        'sale_management',
        'purchase',
        'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/seq_num.xml',
        'data/custom_production_sequence.xml',
        'views/sale_order_view.xml',
        'views/bracket_shapes_view.xml',
        'views/mod_sale_quotation_report.xml',
        'views/inherited_account_move.xml',
        'views/mod_report_invoices.xml',
        'views/purchase_order.xml',
        'views/stock_check.xml',
        'views/inventry_inherit.xml',
        'views/order_processing.xml',
        'wizard/change_product_wizard.xml',
        'reports/report_action.xml',
        'reports/custom_production_report_template.xml',
        'reports/purchase_reports_template.xml',
        'reports/sale_reports_template.xml',

    ],
    'images': ['/static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
