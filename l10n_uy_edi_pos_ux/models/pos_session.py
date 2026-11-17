from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _check_invoices_are_posted(self):
        if self.config_id.l10n_uy_allow_close_with_cfe_error:
            unposted = (
                self._get_closed_orders()
                .sudo()
                .with_company(self.company_id)
                .account_move.filtered(lambda x: x.state != "posted")
            )
            if unposted and not (unposted - unposted._l10n_uy_edi_pos_cfe_error()):
                return
        return super()._check_invoices_are_posted()
