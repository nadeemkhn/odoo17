from odoo import models, fields, api


class Dashboard(models.Model):
    _name = 'my_dashboard.dashboard'
    _description = 'Dashboard Model for OWL'

    name = fields.Char(string="Name", required=True)
    student_count = fields.Integer(string="Number of Students", compute="_compute_student_count")

    @api.depends('student_count')
    def _compute_student_count(self):
        # Yeh query student records ko count karegi
        self.student_count = self.env['school.student'].search_count([])
