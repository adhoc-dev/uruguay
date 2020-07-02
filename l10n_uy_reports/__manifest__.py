# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Uruguay - Accounting Reports',
    'version': '13.0.1.0.0',
    'author': 'ADHOC SA',
    'category': 'Localization',
    'summary': 'Reporting for Uruguayan Localization',
    'description': """
Add VAT Book report which holds the VAT detail info of sales or purchases made in a period of time.
Also add a VAT summary report that is used to analyze invoicing
""",
    'depends': [
        'l10n_uy',
        'account_reports',
    ],
    'data': [
        'data/account_financial_report_data.xml',
        'report/account_uy_vat_line_views.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'demo': [],
    'auto_install': True,
    'installable': True,
}