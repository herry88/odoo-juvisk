#herry prasetyo 2018
from odoo import models, fields, api


class EquipmentMaint(models.Model):
    _inherit ="maintenance.equipment"


    equipment_ids = fields.One2many('battery.rent','equipment_id', string='Equipment Rent')
    use_in_project = fields.Boolean(string='Use In Project', default=False)
    in_use = fields.Boolean(string='Active', default=False)

    @api.multi
    def _area_project(self):
        equipment_data_state =self.env['battery.rent']
        equipment_data_state_area = equipment_data_state.search([('state','=','confirmed')])
        print equipment_data_state_area.name

        if equipment_data_state_area != 'confirmed':
            maintenance_data_area = self.env['maintenance.equipment'].browse(self.equipment_ids.id)
            maintenance_data_area.in_use= False
        else:
            maintenance_data_area.in_use = True
        #
        # print maintenance_data_area.id
        # if equipment_data_state_area :
        #     self.in_use = True



class BatteryRent(models.Model):
    _name = "battery.rent"

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
    ], default='draft')

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






