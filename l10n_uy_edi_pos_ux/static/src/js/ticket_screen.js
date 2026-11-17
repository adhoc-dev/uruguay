import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    l10nUyCanRetryCfe(order) {
        return Boolean(
            order?.finalized &&
                this.pos.config.l10n_uy_cfe_error_flow &&
                this.pos.config.l10n_uy_cfe_error_flow !== "native" &&
                order.l10n_uy_edi_cfe_state === "error"
        );
    },

    async l10nUyRetryCfe(order) {
        const result = await this.pos.data.call("pos.order", "l10n_uy_edi_pos_retry_cfe", [order.id]);
        await this.pos.data.loadServerOrders([["id", "=", order.id]]);
        if (result.cfe_state === "error") {
            this.dialog.add(AlertDialog, {
                title: _t("CFE still not validated"),
                body: _t("DGI did not validate the invoice again:\n\n%s", result.error),
            });
        } else {
            this.dialog.add(AlertDialog, {
                title: _t("CFE validated"),
                body: _t("DGI validated the invoice %s.", result.name),
            });
        }
    },
});
