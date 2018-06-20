# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

to_19_id = ( 'nol',  'satu',   'dua',  'tiga', 'empat',   'lima',   'enam',
          'tujuh', 'delapan', 'sembilan', 'sepuluh',   'sebelas', 'dua belas', 'tiga belas',
          'empat belas', 'lima belas', 'enam belas', 'tujuh belas', 'delapan belas', 'sembilan belas' )
tens_id  = ( 'dua puluh', 'tiga puluh', 'empat puluh', 'lima puluh', 'enam puluh', 'tujuh puluh', 'delapan puluh', 'sembilan puluh')
denom_id = ( '', 'ribu',
	  'juta', 'miliar', 'biliun', 'triliun',       'quadriliun',
          'ribu',     'juta',         'billion',       'trillion',       'quadrillion',
          'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
          'Decillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion' )

def _convert_nn_id(val):
    """ convert a value < 100 to id
    """
    if val < 20:
        return to_19_id[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_id)):
        if dval + 10 > val:
            if val % 10:
                    return dcap + ' ' + to_19_id[val % 10]
            return dcap

def _convert_nnn_id(val):
    """ convert a value < 1000 to id

        special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem == 1:
        word = 'seratus'
        if mod > 0:
            word = word + ' '
    elif rem > 1:
        word = to_19_id[rem] + ' ratus'
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn_id(mod)
    return word

def id_number(val):
    if val < 100:
        return _convert_nn_id(val)
    if val < 1000:
        return _convert_nnn_id(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_id))):
        if dval > val:
	    mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn_id(l) + ' ' + denom_id[didx]
            if r > 0:
                ret = ret + ' ' + id_number(r)
	    if val < 2000:
	        ret = ret.replace("satu ribu","seribu")
	    return ret

def amount_to_text_id(numbers, currency):
    number = '%.2f' % numbers
    units_name = currency
    liste = str(number).split('.')
    start_word = id_number(abs(int(liste[0])))
    end_word = id_number(int(liste[1]))
    cents_number = int(liste[1])
    cents_name = (cents_number > 1) and ' sen' or ' sen'
    final_result = start_word + ' ' + ' rupiah'
    final_result = final_result[:1].upper() + final_result[1:]
    #final_result = units_name + ' ' + start_word + ' ' + end_word + ' ' + cents_name
    return final_result

# class AccountInvoice(models.Model):
#     _inherit = "account.invoice"
#
#     @api.one
#     @api.depends('amount_total')
#     def _amount_in_words(self):
#         self.amount_to_text = amount_to_text_id(self.amount_total, self.currency_id.symbol)
#
#     amount_to_text = fields.Text(string='In Words',
#         store=True, readonly=True, compute='_amount_in_words')

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    @api.depends('amount_total')
    def _amount_in_words(self):
        self.amount_to_text = amount_to_text_id(self.amount_total, self.pricelist_id.currency_id.symbol)
    
    amount_to_text = fields.Text(string='In Words',
        store=True, readonly=True, compute='_amount_in_words')
