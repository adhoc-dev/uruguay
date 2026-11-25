from odoo import api, models

DEMO_POS = "UY e-invoicing POS"


class PosConfig(models.Model):
    _inherit = "pos.config"

    @api.model
    def _l10n_uy_edi_pos_ux_create_demo(self):
        """A POS of the Uruguayan demo company, invoicing with its electronic journal, to try the CFE flows."""
        company = self.env.ref("base.demo_company_uy", raise_if_not_found=False)
        journal = company and self.env["account.journal"].search(
            [("company_id", "=", company.id), ("type", "=", "sale"), ("l10n_uy_edi_type", "=", "electronic")],
            limit=1,
        )
        if not journal or self.search_count([("company_id", "=", company.id), ("name", "=", DEMO_POS)]):
            return
        self = self.with_company(company)
        tax = self.env["account.tax"].search(
            [
                ("company_id", "=", company.id),
                ("type_tax_use", "=", "sale"),
                ("amount", "=", 22),
                ("l10n_uy_tax_category", "=", "vat"),
            ],
            limit=1,
        )
        # Owned by the company, so the prices are in pesos and the POS does not convert them
        self.env["product.product"].create(
            [
                {
                    "name": name,
                    "list_price": price,
                    "company_id": company.id,
                    "taxes_id": [(6, 0, tax.ids)],
                    "available_in_pos": True,
                    "type": "consu",
                }
                for name, price in (("UY POS product", 1000), ("UY POS expensive product", 300000))
            ]
        )
        cash_journal = self.env["account.journal"].create(
            {"name": "Cash UY POS", "type": "cash", "code": "UYPOS", "company_id": company.id}
        )
        payment_method = self.env["pos.payment.method"].create(
            {"name": "Cash", "journal_id": cash_journal.id, "company_id": company.id}
        )
        self.create(
            {
                "name": DEMO_POS,
                "company_id": company.id,
                "invoice_journal_id": journal.id,
                "payment_method_ids": [(6, 0, payment_method.ids)],
            }
        )
