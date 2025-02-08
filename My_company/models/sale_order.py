from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _name = 'medical.sale.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Order'
    _rec_name = 'sequence_sale'



    customer_id = fields.Many2one('medical.customer', string='Customer', required=True)
    medicine_line_ids = fields.One2many('medical.sale.order.line', 'sale_order_id', string='Medicine Lines')
    sale_date = fields.Date('Sale Date', default=fields.Date.today)
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount", store=True)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    sequence_sale = fields.Char(string='Sale Sequence', copy=False, default='New')
    delivery_id = fields.Many2one('stock.delivery', string='Delivery', readonly=True)
    delivery_count = fields.Integer(string='Delivery Count', compute='_compute_delivery_count')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation sent'),
        ('sale', 'Sale Order'),
        ('cancel', 'cancelled'),
        ('done', 'Locked'),

    ],
        default='draft', string='status', tracking=True)

    def get_dashboard_data(self):
        sale_orders = self.search([])  # Get all sale orders
        data = []

        for order in sale_orders:
            data.append({
                'sequence_sale': order.sequence_sale,
                'customer_name': order.customer_id.name,
                'total_amount': order.total_amount,
                'state': order.state,
            })
        return data

    def action_generate_report(self):
        """Button Click par PDF Report Generate karega"""
        return self.env.ref('My_company.report_sale_order').report_action(self)

    @api.constrains('medicine_line_ids')
    def _check_gate_pass_line_ids(self):
        for record in self:
            if not record.medicine_line_ids:
                raise ValidationError("You must add at least one product Quantity")

    @api.onchange('medicine_line_ids')
    def _onchange_medicine_line_ids(self):
        if self.delivery_id:
            for line in self.medicine_line_ids:
                delivery_line = self.env['stock.delivery.line'].search([
                    ('stock_id', '=', self.delivery_id.id),
                    ('product_id', '=', line.medicine_id.id)
                ], limit=1)
                if delivery_line:
                    if line.quantity < delivery_line.demand_qty:
                        raise ValidationError(_(
                            "You cannot reduce the quantity below the delivered amount."
                        ))
                    elif line.quantity != delivery_line.demand_qty:
                        delivery_line.demand_qty = line.quantity

    @api.depends('delivery_id')
    def _compute_delivery_count(self):
        for record in self:
            record.delivery_count = self.env['stock.delivery'].search_count(
                [('id', '=', record.delivery_id.id)])

    def action_sent(self):

    #     self.ensure_one()
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id = ir_model_data._xmlid_lookup('my_company.sale_mail_template')[2]
    #     except (ValueError, IndexError):
    #         template_id = False
    #     try:
    #         compose_form_id = ir_model_data._xmlid_lookup('mail.mail_notification_layout_with_responsible_signature')[2]
    #     except (ValueError, IndexError):
    #         compose_form_id = False
        template = self.env.ref('My_company.sale_mail_template').id
        template_id = self.env['mail.template'].browse(template)
        template_id.send_mail(self.id, force_send=True)



        ctx = {
            'default_model': 'medical.sale.order',
            'default_res_ids': [self.id],  # Updated to use a list
            'default_use_template': True,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }
    # #
    # def create_crm_email_template(self):
    #     body_html = '''
    #                 <p>Hello,</p>
    #                 <p>Your quotation <b>${object.sequence_sale}</b> amounting to <b>${object.total_amount} €</b> is ready for review.</p>
    #                 <p>Do not hesitate to contact us if you have any questions.</p>
    #                 <p>Best regards,</p>
    #                 <p>${object.company_id.name}</p>
    #             '''
    #
    #     template_data = {
    #         'model_id': self.env.ref('my_company.model_medical_sale_order').id,
    #         'name': 'Sale Template',
    #         'subject': 'My Company Quotation (Ref ${object.sequence_sale})',
    #         'body_html': body_html,
    #         'email_from': '${object.company_id.email | safe}',
    #         'email_to': '${object.customer_id.email_formatted}',
    #         'email_to': self.sent,
    #
    #     }

        # email_template = self.env['mail.template'].create(template_data)
        # return email_template

    def acton_done(self):
        self.state = 'done'

    def action_sale(self):
        for order in self:
            stock_delivery_vals = {
                'partner_id': order.customer_id.id,
                'Schedule_date': fields.Date.context_today(self),
                'confirm_date': fields.Date.context_today(self),
                'state': 'draft',
                'picking_type': 'sale',
                'sequence': self.env['ir.sequence'].next_by_code('stock.delivery.sale'),
                'stock_delivery': [
                    (0, 0, {
                        'product_id': line.medicine_id.id,
                        'demand_qty': line.quantity,
                        'done_qty': 0,
                        'price': line.medicine_id.sale_price,
                    }) for line in order.medicine_line_ids
                ]
            }
            delivery = self.env['stock.delivery'].create(stock_delivery_vals)
            order.delivery_id = delivery.id

            order.state = 'sale'

    def action_view_delivery(self):
        self.ensure_one()
        if not self.delivery_id:
            raise ValidationError(_("No delivery record associated with this sale order."))

        return {
            'name': _('Delivery'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.delivery',
            'res_id': self.delivery_id.id,
            'target': 'current',
        }

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        for line in self.medicine_line_ids:
            medicine = line.medicine_id
            medicine.stock += line.quantity
        if self.delivery_id:
            self.delivery_id.state = 'cancel'
        self.state = 'cancel'

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['sequence_sale'] = self.env['ir.sequence'].next_by_code('medical.sale.order') or _("New")

        return super(SaleOrder, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state == 'sale':
                raise ValidationError('you cant delete this because it already confirm')

        return super(SaleOrder, self).unlink()

    @api.depends('medicine_line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.subtotal for line in record.medicine_line_ids)


class SaleOrderLine(models.Model):
    _name = 'medical.sale.order.line'
    _description = 'Sale Order Line'

    sale_order_id = fields.Many2one('medical.sale.order', string='Sale Order', )
    medicine_id = fields.Many2one('medical.medicine', string='Medicine', )
    description = fields.Selection([
    ], string='Medicine_type',related='medicine_id.medicine_type')
    quantity = fields.Integer('Quantity', default=1)
    price = fields.Float('Unit Price', related='medicine_id.sale_price', readonly=True)
    subtotal = fields.Float('Subtotal', compute='_compute_subtotal', store=True)

    def action_generate_report(self):
        """Button Click par PDF Report Generate karega"""
        return self.env.ref('My_company.report_sale_order').report_action(self)

    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price
