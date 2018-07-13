from odoo import models, fields, api

class Mahasiswa(models.Model):
	_name = 'mahasiswa.mahasiswa'

	name = fields.Char('Nama')