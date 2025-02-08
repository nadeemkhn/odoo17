from odoo import models, fields,_



class ReportWizard(models.TransientModel):
    _name = 'sale.order.report.wizard'
    _description = 'Report Wizard'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def print_report(self):
        orders = self.env['medical.sale.order'].search([
            ('sale_date', '>=', self.start_date),
            ('sale_date', '<=', self.end_date),
        ])
        print(f"Orders Fetched: {orders}")
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'docs': orders,
        }
        return self.env.ref('My_company.report_sale_order_wizard').report_action(self, data=data)


