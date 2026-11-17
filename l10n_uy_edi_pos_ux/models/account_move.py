from odoo import models
from odoo.addons.point_of_sale.models.account_move import AccountMove as PosAccountMove

if not getattr(PosAccountMove.button_draft, "_l10n_uy_edi_pos_ux", False):
    _pos_button_draft = PosAccountMove.button_draft

    def button_draft(self):
        """The POS refuses to reset an invoice of an open session; a CFE in error must go back to draft anyway.

        Only that guard is skipped: the rest of the chain runs (l10n_uy_edi clears the temporary name there).
        """
        if self.env.context.get("l10n_uy_edi_pos_force_draft"):
            return super(PosAccountMove, self).button_draft()
        return _pos_button_draft(self)

    button_draft._l10n_uy_edi_pos_ux = True
    PosAccountMove.button_draft = button_draft


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_uy_edi_pos_flow(self):
        self.ensure_one()
        return self.sudo().pos_order_ids[:1].config_id.l10n_uy_cfe_error_flow or "native"

    def _l10n_uy_edi_pos_cfe_error(self):
        return self.filtered(
            lambda m: m.l10n_uy_edi_is_needed and m.sudo().pos_order_ids and m.l10n_uy_edi_cfe_state == "error"
        )

    def _l10n_uy_edi_check_move(self):
        errors = super()._l10n_uy_edi_check_move()
        config = self.sudo().pos_order_ids[:1].config_id
        if config.l10n_uy_simulate_cfe_error and self.company_id.l10n_uy_edi_ucfe_env == "demo":
            errors.append(self.env._("Simulated DGI rejection (PoC): exhausted CAE."))
        return errors

    def _post(self, soft=True):
        if any(move._l10n_uy_edi_pos_flow() == "draft" for move in self):
            self = self.with_context(l10n_uy_edi_pos_force_draft=True)
        res = super()._post(soft=soft)
        # An invoice re-posted once its CFE is accepted gets the payments the POS registered when it was in error.
        for move in res.sudo().filtered(lambda m: m.country_code == "UY" and m.pos_order_ids):
            payment_moves = move.pos_order_ids.payment_ids.account_move_id
            receivable = move.line_ids.filtered(lambda line: line.account_type == "asset_receivable")
            if payment_moves and not any(receivable.mapped("reconciled")):
                move.pos_order_ids[:1]._reconcile_invoice_payments(move, payment_moves)
        return res

    def _generate_and_send(self, force_synchronous=True, allow_fallback_pdf=True, **custom_settings):
        cfe_error = self._l10n_uy_edi_pos_cfe_error().filtered(lambda m: m._l10n_uy_edi_pos_flow() != "native")
        cfe_error.filtered(
            lambda m: m.state == "posted" and m._l10n_uy_edi_pos_flow() == "posted_then_draft"
        ).with_context(l10n_uy_edi_pos_force_draft=True).button_draft()
        return super(AccountMove, self - cfe_error)._generate_and_send(
            force_synchronous=force_synchronous, allow_fallback_pdf=allow_fallback_pdf, **custom_settings
        )
