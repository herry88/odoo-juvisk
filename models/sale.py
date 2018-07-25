from odoo import models, fields, api

class SaleLine(models.Model):
    _inherit = 'sale.order.line'

    project_id = fields.Many2one('project.project', compute='compute_project_id')

    @api.one
    # @api.depend('analytic_account_id')
    def compute_project_id(self):
        project_id = selv.env['project.project'].search([('analytic_account_id','=',self.analytic_account_id.id)],limit=1)
        self.project_id = project_id and project_id.id or False
