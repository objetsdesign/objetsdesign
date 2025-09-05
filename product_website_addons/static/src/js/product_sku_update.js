/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSale.include({

    /**
     * On ajoute la référence interne au dictionnaire combinationInfo
     */
    async _getCombinationInfo(ev) {
        const combinationData = await super._getCombinationInfo(ev);
        const productId = combinationData.product_id;

        if (productId) {
            const productData = await this.rpc('/shop/get_variant_default_code', {
                product_id: productId,
            });
            combinationData.default_code = productData.default_code || '';
        }

        return combinationData;
    },
});
