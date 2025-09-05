import { patch } from "@web/core/utils/patch";
import { ProductConfiguratorDialog } from "./product_configurator_dialog/product_configurator_dialog";

patch(ProductConfiguratorDialog.prototype, {
    async _onChangeCombination(event, parent, combination) {
        // Appel de la fonction parent
        await super._onChangeCombination(event, parent, combination);

        // Met à jour la référence du produit
        const reference = parent.find(".product_reference");
        console.log(reference)
        if (combination.default_code) {
            reference.text(`Référence : {combination.default_code}`).show();
        } else {
            reference.hide();
        }
    },
});
