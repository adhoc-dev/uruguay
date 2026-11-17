from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    l10n_uy_cfe_error_flow = fields.Selection(
        [
            ("native", "Current behaviour"),
            ("draft", "PoC 1: invoice in draft, payment not reconciled"),
            ("posted_then_draft", "PoC 2: invoice reconciled and back to draft"),
        ],
        string="Flow when the CFE fails",
        default="native",
        required=True,
        help="PoC only: what happens to the invoice of a sale when DGI does not validate its CFE.\n"
        "- Current behaviour: the invoice stays posted, without number, and the POS downloads a proforma.\n"
        "- PoC 1: the invoice goes back to draft, the payment is reconciled when the invoice is posted again.\n"
        "- PoC 2: the invoice is posted and reconciled as usual, then goes back to draft.\n"
        "In both PoC the cashier is warned and can retry the CFE from the order list.",
    )
    l10n_uy_allow_close_with_cfe_error = fields.Boolean(
        string="Close with CFE in error",
        help="Allow closing the session when some invoices are in draft because their CFE was not validated in DGI.",
    )
    l10n_uy_check_final_consumer_limit = fields.Boolean(
        string="Check the final consumer limit",
        help="Before paying, the POS asks for an identified customer when the sale exceeds the amount DGI allows "
        "for an unidentified one (5000 UI), instead of letting the CFE fail.",
    )
    l10n_uy_final_consumer_limit = fields.Monetary(
        string="Final consumer limit",
        compute="_compute_l10n_uy_final_consumer_limit",
        currency_field="currency_id",
    )
    l10n_uy_simulate_cfe_error = fields.Boolean(
        string="Simulate a DGI error",
        help="PoC only, and only with Uruware in demo mode: every CFE of this POS fails as if DGI had rejected it "
        "(for example, exhausted CAE).",
    )

    @api.depends("company_id")
    def _compute_l10n_uy_final_consumer_limit(self):
        edi_document = self.env["l10n_uy_edi.document"]
        today = fields.Date.context_today(self)
        for config in self:
            company = config.company_id
            config.l10n_uy_final_consumer_limit = (
                company.country_code == "UY" and edi_document._get_minimum_legal_amount(company, today)
            )

    @api.model
    def _l10n_uy_edi_pos_ux_create_demo(self):
        """One POS per flow, so each one can be tried side by side."""
        company = self.env.ref("base.demo_company_uy", raise_if_not_found=False)
        journal = company and self.env["account.journal"].search(
            [("company_id", "=", company.id), ("type", "=", "sale"), ("l10n_uy_edi_type", "=", "electronic")],
            limit=1,
        )
        if not journal or self.search_count([("company_id", "=", company.id), ("name", "=like", "PoC CFE%")]):
            return
        self = self.with_company(company)
        company.l10n_uy_edi_ucfe_env = "demo"
        tax = self.env["account.tax"].search(
            [
                ("company_id", "=", company.id),
                ("type_tax_use", "=", "sale"),
                ("amount", "=", 22),
                ("l10n_uy_tax_category", "=", "vat"),
            ],
            limit=1,
        )
        products = self.env["product.product"].create(
            [
                {"name": "PoC CFE: product", "list_price": 1000},
                {"name": "PoC CFE: expensive product", "list_price": 300000},
            ]
        )
        products.write({"taxes_id": [(6, 0, tax.ids)], "available_in_pos": True, "type": "consu"})
        flows = [
            ("PoC CFE 0 - Current behaviour", {"l10n_uy_cfe_error_flow": "native"}),
            ("PoC CFE 1 - Draft", {"l10n_uy_cfe_error_flow": "draft"}),
            (
                "PoC CFE 1 - Draft, can close",
                {"l10n_uy_cfe_error_flow": "draft", "l10n_uy_allow_close_with_cfe_error": True},
            ),
            ("PoC CFE 2 - Back to draft", {"l10n_uy_cfe_error_flow": "posted_then_draft"}),
            (
                "PoC CFE 2 - Back to draft, final consumer limit",
                {"l10n_uy_cfe_error_flow": "posted_then_draft", "l10n_uy_check_final_consumer_limit": True},
            ),
            (
                "PoC CFE 2 - Back to draft, DGI error",
                {"l10n_uy_cfe_error_flow": "posted_then_draft", "l10n_uy_simulate_cfe_error": True},
            ),
        ]
        for index, (name, values) in enumerate(flows, start=1):
            cash_journal = self.env["account.journal"].create(
                {"name": f"Cash {name}", "type": "cash", "code": f"PCF{index}", "company_id": company.id}
            )
            payment_method = self.env["pos.payment.method"].create(
                {"name": "Cash", "journal_id": cash_journal.id, "company_id": company.id}
            )
            self.create(
                {
                    "name": name,
                    "company_id": company.id,
                    "invoice_journal_id": journal.id,
                    "payment_method_ids": [(6, 0, payment_method.ids)],
                    **values,
                }
            )
