from odoo import models, fields, api

class ProjectSite(models.Model):
     _name = 'project.site'

     site_id = fields.Char(string="Site ID", readonly=True)
     name = fields.Char(string="Site Name", require=True)
     alias = fields.Char(string="Site Alias")
     tower_type_id = fields.Many2one('project.tower.type', string="Tower Type")
     region_id = fields.Many2one('project.region', string="Region")
     area_id = fields.Many2one('project.area', string="Area")
     type_id = fields.Many2one('project.type', string="Type")
     address = fields.Text()

     @api.model
     def create(self, vals):
          vals['site_id'] = self.env['ir.sequence'].next_by_code('project.site') or '/'
          return super(ProjectSite, self).create(vals)

class ProjectTowerType(models.Model):
     _name = 'project.tower.type'

     name = fields.Char(string="Tower Type", require=True)

class ProjectRegion(models.Model):
     _name = 'project.region'

     name = fields.Char(string="Region", require=True)

class ProjectArea(models.Model):
     _name = 'project.area'

     name = fields.Char(string="Area", require=True)

class ProjectType(models.Model):
     _name = 'project.type'

     name = fields.Char(string="Type", require=True)
