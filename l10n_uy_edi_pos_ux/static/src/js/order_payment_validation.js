import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { formatCurrency } from "@web/core/currency";

patch(OrderPaymentValidation.prototype, {
    l10nUyCfeErrorFlowEnabled() {
        return this.pos.config.l10n_uy_cfe_error_flow && this.pos.config.l10n_uy_cfe_error_flow !== "native";
    },

    l10nUyIsIdentified(partner) {
        // The receiver data DGI asks for above the final consumer limit
        return Boolean(
            partner?.vat && partner.street && partner.city && partner.state_id && partner.country_id
        );
    },

    async askBeforeValidation() {
        const result = await super.askBeforeValidation(...arguments);
        if (result === false) {
            return false;
        }
        const config = this.pos.config;
        if (
            config.l10n_uy_check_final_consumer_limit &&
            config.l10n_uy_final_consumer_limit &&
            this.order.priceIncl > config.l10n_uy_final_consumer_limit &&
            !this.l10nUyIsIdentified(this.order.getPartner())
        ) {
            this.pos.dialog.add(AlertDialog, {
                title: _t("Identified customer required"),
                body: _t(
                    "This sale exceeds the amount DGI allows for an unidentified customer (%(limit)s).\nSelect a customer with ID number, address, city, state and country before paying.",
                    { limit: formatCurrency(config.l10n_uy_final_consumer_limit, this.pos.currency.id) }
                ),
            });
            return false;
        }
        return result;
    },

    shouldDownloadInvoice() {
        // Without a CFE validated by DGI there is no legal PDF: do not download a proforma
        if (this.l10nUyCfeErrorFlowEnabled() && this.order.l10n_uy_edi_error) {
            return false;
        }
        return super.shouldDownloadInvoice(...arguments);
    },

    async finalizeValidation() {
        const result = await super.finalizeValidation(...arguments);
        if (this.l10nUyCfeErrorFlowEnabled() && this.order.l10n_uy_edi_error) {
            this.pos.dialog.add(AlertDialog, {
                title: _t("CFE not validated in DGI"),
                body: _t(
                    "The sale was registered, but DGI did not validate its invoice, so it has no number or PDF yet.\nOnce the problem is solved, retry it from Orders: select the order and press Retry CFE.\n\n%s",
                    this.order.l10n_uy_edi_error
                ),
            });
        }
        return result;
    },
});
