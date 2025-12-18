from odoo import models,fields

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def sell_property(self):
        res = super().sell_property()

        for record in self:

            self.env["account.move"].create({
                "partner_id": record.buyer_id.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (0, 0, {
                        "name": "6% Commission",
                        "quantity": 1,
                        "price_unit": record.selling_price * 0.06,
                    }),
                    (0, 0, {
                        "name": "Administrative Fees",
                        "quantity": 1,
                        "price_unit": 100.0,
                    }),
                ],
            })

        return res