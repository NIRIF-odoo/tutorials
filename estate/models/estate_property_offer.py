from odoo import api,models,fields
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(selection=[('accepted','Accepted'),('refused','Refused')], copy=False)
    partner_id = fields.Many2one('res.partner',required=True)
    property_id = fields.Many2one('estate.property',required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one("estate.property.type",related="property_id.property_type_id", store=True)



    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = create_date + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = (record.date_deadline - create_date).days


    def accept_property(self):
        for record in self:
            if record.property_id.offer_ids.filtered(lambda x: x.status == "accepted"):
                raise UserError("An offer has already been accepted for this property!")
            record.status = 'accepted'
            record.property_id.write({
                "buyer_id" : record.partner_id.id,
                "selling_price" : record.price,
                "state":"offer_accepted",
              })
    
    def refuse_property(self):
        for record in self:
            if record.status == 'accepted':
                raise UserError("Accepted properties cannot be refused!")
            else:
                record.status = 'refused'


    _check_offer_price = models.Constraint(
        'CHECK(price > 0)',
        'The offer price must be strictly positive',
    )


    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            property_id = vals.get('property_id')
            if not property_id:
                continue

            property_rec = self.env['estate.property'].browse(property_id)

            offer_price = vals.get('price')
            if offer_price and property_rec.offer_ids:
                max_offer = max(property_rec.offer_ids.mapped('price'))
                if offer_price < max_offer:
                    raise UserError(
                        "You cannot create an offer lower than an existing offer."
                    )

            if property_rec.state == 'new':
                property_rec.state = 'offer_received'

        return super().create(vals_list)