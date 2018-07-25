from odoo import models, fields, api

class EquipmentMaint(models.Model):
    _inherit ="maintenance.equipment"


    equipment_ids = fields.One2many('battery.rent','equipment_id', string='Equipment Rent')
    equipment_project = fields.One2many('project.project','equipment_id',string='Equipment Project')
    equipment_site = fields.One2many('project.site','equipment_id', string='Equipment Site')
    equipment_area = fields.One2many('project.area','equipment_id', string='Equipment Area')
    use_in_project = fields.Boolean(string='Use In Project', default=False)
    in_use = fields.Char(string='Active', compute='_area_active')
    project_name = fields.Char( string='Project Name', compute='_project_name')
    site_id = fields.Char(string='Site Name',compute='_project_id_data')
    site_owner_name = fields.Char(string='Site Name Owner',compute='_project_name_owner')
    site_area = fields.Char(string='Project Area',compute='_project_area_area')

    @api.one
    def _project_id_data(self):
        project_id_data = self.env['project.project'].search([('equipment_id','=',self.equipment_site.id)], limit=1)
        self.site_id = project_id_data and project_id_data.site_id.name or False
        # print project_id_data

    @api.one
    def _project_name_owner(self):
        project_name_owner = self.env['project.project'].search([('equipment_id','=',self.equipment_project.id)], limit=1)
        self.site_owner_name = project_name_owner and project_name_owner.site_name_owner or False
        # print project_id_data

    @api.one
    def _project_area_area(self):
        project_name_area = self.env['project.area'].search([('equipment_id','=',self.equipment_area.id)], limit=1)
        self.site_area = project_name_area and project_name_area.name or False
        # print project_id_data

    @api.one
    def _project_name(self):
        project_area_battery = self.env['battery.rent'].search([('equipment_id','=',self.equipment_ids.id)])
        self.project_name = project_area_battery and project_area_battery.name or False
        # for data in project_area_battery :
        #     self.project_area =  data.project_id.name

    @api.one
    def _area_active(self):
        area_project = self.env['battery.rent'].search([('state','=','confirmed'),('equipment_id','=',self.equipment_ids.ids or [])])

        for data in area_project :
            if data :
               self.in_use = 'Active'
            else :
               self.in_use = 'Deactive'

            print area_project



class BatteryRent(models.Model):
    _name = "battery.rent"
    _inherit = ['mail.thread']

    project_id = fields.Many2one('project.project',string='Project Name')
    equipment_id = fields.Many2one('maintenance.equipment',string='Equipment Name')
    name = fields.Char(string='Reference')
    plan_start_date = fields.Date('Plan Start Date')
    plan_done_date  = fields.Date('Plan Done Date')
    actual_start_date = fields.Date('Actual Start Date')
    actual_done_date = fields.Date('Actual Done Date')
    remark = fields.Text(string='Remark')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('done', "Done"),
    ], string='Status', readonly=True, copy=False, default='draft', track_visibility='onchange')

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        print 'action_draft_running'
        # TODO : ubah status equioment field use_in_project dari true ke false
        # cek equipment_id sudah ada tidak null
        # buat koneksi ke model maintenance equipment
        # cari data maintenance equipment berdasarkan equipment_id
        # jika ditemukan maka
        # ubah status equioment field use_in_project dari true ke false
        if self.equipment_id :
            maintenance_equipment_pool = self.env['maintenance.equipment']
            equipment_data = maintenance_equipment_pool.browse(self.equipment_id.id)
            equipment_data.use_in_project = False

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
        # TODO:
        # cek equipment_id sudah ada tidak null
        # buat koneksi ke model maintenance equipment
        # cari data maintenance equipment berdasarkan equipment_id
        # jika ditemukan maka
        # Ubah status equipment fields use_in_project false to true
        if self.equipment_id :
            maintenance_equipment_pool = self.env['maintenance.equipment']
            equipment_data = maintenance_equipment_pool.browse(self.equipment_id.id)
            equipment_data.use_in_project = True


    @api.multi
    def action_done(self):
        self.state = 'done'
        print 'action_done_running'
        # TODO : ubah status equioment field use_in_project dari true ke false
        # cek equipment_id sudah ada tidak null
        # buat koneksi ke model maintenance equipment
        # cari data maintenance equipment berdasarkan equipment_id
        # jika ditemukan maka
        # ubah status equioment field use_in_project dari true ke false
        if self.equipment_id :
            maintenance_equipment_pool = self.env['maintenance.equipment']
            equipment_data = maintenance_equipment_pool.browse(self.equipment_id.id)
            equipment_data.use_in_project = False

    #field function



    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('battery.rent') or '/'
        vals['name'] = seq
        result = super(BatteryRent, self).create(vals)
        return  result

class TemporaryClass (models.Model):
    _name = 'battery.rent.move'







