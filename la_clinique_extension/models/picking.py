from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

import json
from lxml import etree

class StockMove(models.Model):
	_inherit = "stock.move"

	@api.depends('product_uom_qty','reserved_availability')
	def _compute_missing_qty(self):
		for order in self:
			order.missing_qty = order.product_uom_qty - order.reserved_availability

	def _compute_moc_doc_ref(self):
		for ref in self:
			ref.moc_doc_ref = ref.picking_id.sale_id.moc_doc_ref

	missing_qty = fields.Float(string='Missing Qty',compute="_compute_missing_qty",copy=False)
	moc_doc_ref = fields.Char(string="Moc Doc Ref",compute="_compute_moc_doc_ref")

	def delivery_order_lines(self):
		outgoing_moves = self.env['stock.move'].search([('picking_id.picking_type_id.code', '=', 'outgoing'),
			('picking_id.state', 'not in', ('done','cancel')),
			('picking_id.sale_id.name', 'ilike', 'S')])

		new_outgoing_moves = []
		for move in outgoing_moves:
			if move.product_uom_qty != move.quantity_done and move.missing_qty > 0.0:
				new_outgoing_moves.append(move.id)

		view_id = self.env.ref('la_clinique_extension.view_delivery_order_lines_tree_new').id

		action = {
			'type': 'ir.actions.act_window',
			'name': 'Pending Delivery Lines',
			'res_model': 'stock.move',
			'view_mode': 'tree',
			'views': [(view_id, 'tree')],
			'domain': [('id', 'in', new_outgoing_moves)],
			'context':{},
		}
		return action
