from odoo import models, fields

class TodoTask(models.Model):
    _name = 'todo.app'
    _description = 'To-Do Task'

    name = fields.Char(string='Task Name', required=True)
    completed = fields.Boolean(string='Completed')
    color = fields.Char(string='Color')
