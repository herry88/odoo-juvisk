from odoo import models, fields, api

class ProjectEquipment(models.Model):
    _inherit = "project.project"

    project_ids = fields.One2many('battery.rent','project_id', ondelete='cascade', index= True, string='Project Reference')
    # in_use = fields.Boolean(string='Use In Project', default=False)



    # equipment_id = fields.Many2one('maintenance.equipment', ondelete='cascade', index=True, string='Equipment Reference')
    # # area_id = fields.Related('site_id', 'area_id', type='many2one', relation='project.area',string='Area', store=True)

    # @api.multi
    # def write(self, data):
    #     print '=============='
    #     print data
    #     if data.get('project_ids'):
    #         print data.get('project_ids')
    #         row_num = 0
    #         for val in data.get('project_ids'):
    #             print row_num
    #             # print val[2]
    #             if str(val[2]) == 'False':
    #                 print  val[2]
    #             row_num += 1
    #
    #     record = super(ProjectEquipment, self).write(data)
    #     return record
