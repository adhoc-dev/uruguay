import { InvoiceButton } from "@point_of_sale/app/screens/ticket_screen/invoice_button/invoice_button";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(InvoiceButton.prototype, {
    async _downloadInvoice(orderId) {
        const order = this.pos.models["pos.order"].get(orderId);
        const flow = this.pos.config.l10n_uy_cfe_error_flow;
        if (flow && flow !== "native" && order?.l10n_uy_edi_cfe_state === "error") {
            // Without a CFE validated by DGI there is no legal PDF: do not download a proforma
            this.dialog.add(AlertDialog, {
                title: _t("Invoice PDF not available"),
                body: _t("DGI did not validate this invoice yet. Retry the CFE first."),
            });
            return order;
        }
        return super._downloadInvoice(...arguments);
    },
});
