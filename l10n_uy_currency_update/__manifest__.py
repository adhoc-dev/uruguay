##############################################################################
#
#    Copyright (C) 2022  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Uruguayan Currency Rate Update',
    'version': '13.0.1.0.0',
    'category': 'Localization/Uruguay',
    'sequence': 14,
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'summary': '',
    'depends': [
        'currency_rate_live',
        'l10n_uy_account',
    ],
    'external_dependencies': {
        'python': ['pyOpenSSL', 'zeep']
    },
    'data': [
        'data/ir_cron_data.xml',
        'data/res_company_data.xml',
        'data/res.currency.csv',
        'views/res_currency_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}