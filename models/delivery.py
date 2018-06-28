from odoo import models, fields, api


class PickingSlip (models.Model):
    _inherit = "stock.picking"

    partner_ref = fields.Char(sting='Vendor Ref', compute='_compute_partner_ref')

    def _compute_partner_ref(self):
        # define obj purchase order
        # find purchase order based on name and stock picking origin
        # get requisition ID in purchase order save to self.partner_ref

        print self.origin
        purchase_order_data = self.env['purchase.order'].search([('name','=',self.origin)])
        for data in purchase_order_data:
            self.partner_ref = data.partner_ref
            print data
