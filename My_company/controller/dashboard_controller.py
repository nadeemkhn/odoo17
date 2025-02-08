from odoo import http
from odoo.http import request

class DashboardController(http.Controller):
    @http.route('/dashboard', type='json', auth='user')
    def get_dashboard_data(self):
        # Fetch data from model
        sale_order_obj = request.env['medical.sale.order']
        data = sale_order_obj.get_dashboard_data()
        return data