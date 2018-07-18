from odoo import models, fields, api

class Budget(models.Model):
    _inherit = 'crossovered.budget'

    scope_id = fields.Many2one('project.scope', string="Scope of Work", required=True)
    project_id = fields.Many2one('project.project', string="Project",required=True)
    crossovered_budget_line = fields.One2many('crossovered.budget.lines', 'crossovered_budget_id', 'Budget Lines',
        states={'done': [('readonly', True)]}, copy=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('approve', 'Approved'),
        ('done', 'Done')
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    validate_by = fields.Many2one('res.users', string='Manager Approve')
    approve_by = fields.Many2one('res.users', string='Director Approve')

    @api.multi
    def action_budget_validate(self):
        self.write({'state': 'validate','validate_by':self.env.uid})

    @api.multi
    def action_budget_approve(self):
        self.write({'state': 'approve','approve_by':self.env.uid})

    @api.onchange('project_id', 'scope_id', 'date_from', 'date_to')
    def _onchange_name(self):
        # generate project name from scope and site name
        if self.project_id and self.scope_id and self.date_from and self.date_to:

            budget_scope = self.env['budget.template'].search([('scope_id', '=', self.scope_id.id)])
            vals = []
            for lines in budget_scope:

                vals.append({'general_budget_id': lines.general_budget_id.id,
                             'analytic_account_id': self.project_id.analytic_account_id.id,
                             'date_from': self.date_from,
                             'date_to': self.date_to,
                             'planned_amount':0,
                             })
            #print vals
            self.crossovered_budget_line = vals


class BudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    residual = fields.Float(compute='_compute_residual', string="Residual", digits=0)

    @api.multi
    def _compute_residual(self):

        for line in self:
            line.residual = line.planned_amount + line.practical_amount


class BudgetTemplate(models.Model):
    _name = 'budget.template'

    name = fields.Char(string="Budget Detail", required=True)
    scope_id = fields.Many2one("project.scope", string="Scope", required=True)
    priority = fields.Integer(string="Priority", required=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position', required=True)


class SaleOrderLineAnalytic(models.Model):
    _inherit = "sale.order.line"

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    #add analytic account when generate invoice from sale order
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res
