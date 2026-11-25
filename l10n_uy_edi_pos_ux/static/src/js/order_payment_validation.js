import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { CfeErrorDialog } from "./cfe_error_dialog";

patch(OrderPaymentValidation.prototype, {
    l10nUyIsUruguayan() {
        return this.pos.company.country_id?.code === "UY";
    },

    shouldDownloadInvoice() {
        // The PDF of Uruware is asked only when the cashier prints the invoice
        if (this.l10nUyIsUruguayan()) {
            return false;
        }
        return super.shouldDownloadInvoice(...arguments);
    },

    async finalizeValidation() {
        const result = await super.finalizeValidation(...arguments);
        if (this.l10nUyIsUruguayan() && this.order.l10n_uy_edi_error) {
            this.pos.dialog.add(CfeErrorDialog, {
                title: _t("Sale registered, but its tax receipt was not issued"),
                message: _t(
                    "The sale was registered, but its tax receipt (CFE) was not issued because of an error, so there is nothing to print. Ask your supervisor to fix the tax receipt from the backend. To do so, give them the order number: %s",
                    this.order.pos_reference
                ),
                error: this.order.l10n_uy_edi_error,
            });
        }
        return result;
    },
});
