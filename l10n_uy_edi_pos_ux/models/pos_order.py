from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    l10n_uy_edi_cfe_state = fields.Selection(related="account_move.l10n_uy_edi_cfe_state")
    l10n_uy_edi_error = fields.Text(related="account_move.l10n_uy_edi_error")

    def _reconcile_invoice_payments(self, invoice, payment_moves):
        # A draft invoice (CFE in error) is reconciled when it is posted again.
        if invoice.state != "posted":
            return
        return super()._reconcile_invoice_payments(invoice, payment_moves)

    def l10n_uy_edi_pos_retry_cfe(self):
        """Called from the POS order list: sends again the CFE of an invoice that DGI did not validate."""
        self.ensure_one()
        invoice = self.sudo().account_move
        if invoice.state == "draft" and invoice._l10n_uy_edi_pos_cfe_error():
            invoice.with_context(l10n_uy_edi_pos_force_draft=True).action_post()
            if invoice.state == "posted":
                # Same as a sale that went fine: the invoice gets its PDF and is sent.
                invoice._generate_and_send()
        return {
            "state": invoice.state,
            "cfe_state": invoice.l10n_uy_edi_cfe_state,
            "error": invoice.l10n_uy_edi_error or False,
            "name": invoice.name or False,
        }
