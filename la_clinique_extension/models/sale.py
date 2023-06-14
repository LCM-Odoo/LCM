from odoo import api, fields, models, SUPERUSER_ID, _
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    create_api_values = fields.Char(string='Create API Values',copy=False)
    make_so_readonly = fields.Boolean(string='Make SO Readonly',copy=False)
    moc_doc_ref = fields.Char(string="Moc Doc Ref",copy=False)
    patient_type = fields.Selection(selection=[('in', 'In-Patient'),('out', 'Out-Patient')], string='Patient Type',copy=False, tracking=True,default='')

    insurance_provider_id = fields.Many2one('insurance.provider',string="Insurance Company",copy=False)
    agreed_amount = fields.Float(string="Agreed Amount",copy=False)
    actual_paid = fields.Float(string="Actual Paid",copy=False)


    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        return result

    def write(self, values):
        result = super(SaleOrder, self).write(values)
        return result

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['inv_insurance_provider_id'] = self.insurance_provider_id.id if self.insurance_provider_id else ''
        invoice_vals['inv_agreed_amount'] = self.agreed_amount if self.agreed_amount else 0.0
        invoice_vals['inv_actual_paid'] = self.actual_paid if self.actual_paid else 0.0
        invoice_vals['inv_moc_doc_ref'] = self.moc_doc_ref if self.moc_doc_ref else False
        return invoice_vals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    moc_doc_location_id = fields.Many2one('stock.location',string='Moc doc Location')

    def _prepare_invoice_line(self, **optional_values):
        values = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        values.update({'moc_doc_ref':self.order_id.moc_doc_ref if self.order_id.moc_doc_ref else False})
        return values

    # 1.This fucntion will pass the P&D value from SO Line To Stock Move P&D Line

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({'moc_location_id':self.moc_doc_location_id.id if self.moc_doc_location_id else False})
        return values


class StockMove(models.Model):
    _inherit = "stock.move"

    move_moc_doc_location_id = fields.Many2one('stock.location',string='Moc doc Location')

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        res.update({
            'is_from_api': True if self.group_id.sale_id and self.group_id.sale_id.create_api_values else False,
            })
        return res

    @api.model
    def create(self, vals):    
        result = super(StockMove, self).create(vals)
        return result


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_from_api = fields.Boolean(string='From Api',copy=False)
    moc_doc_ref = fields.Char(string="Moc Doc Ref",copy=False)
    create_api_values = fields.Char(string='Internal Transfer Create API Values',copy=False)
    

    def action_assign(self):
        values = super(StockPicking, self).action_assign()
        if self.is_from_api:
            for i in self.move_line_ids_without_package:
                if i.move_line_moc_doc_location_id:
                    i.location_id = i.move_line_moc_doc_location_id.id
        return values


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id,values)
        res.update({'move_moc_doc_location_id': values.get('moc_location_id') if values.get('moc_location_id') else ''})
        return res



class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    move_line_moc_doc_location_id = fields.Many2one('stock.location',related='move_id.move_moc_doc_location_id',string='Moc doc Location')






