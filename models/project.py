from odoo import models, fields, api

class ProjectEquipment(models.Model):
    _inherit = "project.project"

    project_ids = fields.One2many('battery.rent','project_id', ondelete='cascade', index= True, string='Project Reference')
    in_use = fields.Char(string='Use In Project')
    equipment_id = fields.Many2one('maintenance.equipment',string='Equipment Name')
    site_name_owner = fields.Char(string='Site Name Owner')
    site_id_customer = fields.Char(string='Site Id Customer')
    area_project = fields.Char(string='Project Area')

    customer_name = fields.Char(string="Customer ID")
    project_id = fields.Char(string="Project ID")
    company_id = fields.Many2one('res.company', 'Company', required=True,index=True,
                                 default=lambda self: self.env.user.company_id.id )
    operator_id = fields.Many2one('project.operator', string="Operator", required=True)
    scope_id = fields.Many2one('project.scope', string="Scope of Work", required=True)
    site_id = fields.Many2one('project.site', string="Site",required=True)
    target_rfi = fields.Date(string='Date RFI')

    @api.model
    def create(self, vals):
        vscope_id = vals['scope_id']
        vcomp_id = vals['company_id']
        #add company mark/code on project id
        obj_company = self.env['res.company'].browse([vcomp_id])
        for tcomp in obj_company:
            vcomp = tcomp.name[:1]
        #generate next sequence depend on project scope
        obj_scope_seq = self.env['project.scope'].browse([vscope_id])
        for tseq in obj_scope_seq:
            vals['project_id'] = vcomp +"-"+tseq.sequence_id.next_by_id()
            vals['name'] = vals['project_id'] +" - "+ vals['name']

        return super(ProjectEquipment, self).create(vals)

    @api.onchange('site_id','scope_id')
    def _onchange_name(self):
        # generate project name from site name
        if self.site_id and self.scope_id:
            self.name = self.site_id.name

class Operator(models.Model):
    _name = 'project.operator'

    name = fields.Char(string="Operator Name")

class Scope(models.Model):
    _name = 'project.scope'

    name = fields.Char(string="Scope of Work", required=True)
    code = fields.Char(string="Code", required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence', readonly=True)

    @api.model
    def create(self, vals):
        # create and update sequence_id with ir.sequence new record before
        vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        return super(Scope, self).create(vals)

    @api.model
    def _create_sequence(self, vals, refund=False):

        seq = {
            'name': 'project ' + vals['name'],
            'implementation': 'no_gap',
            'prefix': vals['code']+'%(y)s',
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
        }

        return self.env['ir.sequence'].create(seq)

