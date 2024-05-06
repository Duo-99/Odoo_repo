from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from io import BytesIO
import xlsxwriter
import base64



class bee_confg(models.Model):
    _name = 'bee.confg'
    _description = 'bee_confg'

    tr_date = fields.Date(string = 'Transport_Date', default = fields.Date.today)
    rc_date = fields.Date(string = 'Expeceted_Receive', default = fields.Date.today)
    
    
    option1 = fields.Boolean(string='Bike')
    option2 = fields.Boolean(string='Shipping')
    option3 = fields.Boolean(string='Airways')
    selected_option = fields.Selection([('option1', 'Bike'), 
                                         ('option2', 'Shipping'), 
                                         ('option3', 'Airways')], 
                                        string='Selected_Way', 
                                        compute='_compute_selected_option',
                                        store=True)

    @api.depends('option1', 'option2', 'option3')
    def _compute_selected_option(self):
        for record in self:
            if record.option1 and not (record.option2 or record.option3):
                record.selected_option = 'option1'
            elif record.option2 and not (record.option1 or record.option3):
                record.selected_option = 'option2'
            elif record.option3 and not (record.option1 or record.option2):
                record.selected_option = 'option3'
            else:
                record.selected_option = False

    @api.constrains('selected_option')
    def _check_selected_option(self):
        for record in self:
            if not record.selected_option:
                raise ValidationError('Please choose exactly one option.')
    
    @api.constrains('selected_option')
    def _check_selected_semester(self):
        for record in self:
            if record.selected_option:
                selected_semester_count = sum(1 for rec in self if rec.selected_option)
                if selected_semester_count > 1:
                    raise ValidationError('You can only select one semester.')
    
    

    
    request = fields.Text()
    products = fields.Many2many('stock.picking', string = "Transfer")
    
    ref = fields.Char('Reference',related='products.name')
    contact = fields.Many2one(related='products.partner_id',string="Contact")

# -----------------------------------------------------------
    
    
    
    
    
    
    
    
    
    
    
    
class delivery_type(models.Model):
    _inherit = 'stock.picking'
    
    type = fields.Many2one('bee.confg.delivery',string = "Delivery Type")
    
    
class delivery_type_1(models.Model):
    _name = 'bee.confg.delivery'
    _description = 'bee_confg_delivery'
    
    type = fields.Char(string = "Delivery Type (Bike,Airways,Shipping)",default = "Bike",required = True)
    available = fields.Boolean(string = "Available",default = True)
    name = fields.Char(string = "Delivery ID",required = True,default = "Bike - 00")
    

    
    
class delivery_detail(models.TransientModel):
    _name = 'bee_inventory.detail'
    _description = 'bee_confg'
    
    
    tr_date = fields.Date(string = 'Start Date',required=True)
    rc_date = fields.Date(string = 'End Date',required = True)
    vendor = fields.Many2many('res.partner')
    name = fields.Char(related='vendor.translated_display_name')
    picking_record = fields.Many2many('stock.picking',compute='_filter_picking_records')
    
    def generate_report(self):
        return self.env.ref('bee_inventory.reports_2').report_action([])
    def generate_xlsx_report(self):
        return self.env.ref('bee_inventory.reports_3').report_action([])
    
    def _filter_picking_records(self):
     for record in self:
        contact = [v.translated_display_name for v in record.vendor]
        domain = []
        if record.tr_date:
            domain.append(('scheduled_date','>=',record.tr_date))
        if record.rc_date:
            domain.append(('scheduled_date','<=',record.rc_date))
        if contact:
            domain.append(('partner_id','in',contact))
        pickings = self.env['stock.picking'].search(domain)
        record.picking_record = pickings
        
        
        
        

class ExcelReport(models.AbstractModel):
    _name = 'report.bee_inventory.reports_3'
    _inherit = "report.report_xlsx.abstract"
    
    def generate_xlsx_report(self, workbook, data, lines):
        # Create header format
        header_format = workbook.add_format({
            'font_size': 18,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        label_format = workbook.add_format({
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        line_format = workbook.add_format({
            'font_size': 12,
        })
        
        # Add a new worksheet for the report
        sheet = workbook.add_worksheet('Delivery Detail')
        
        sheet.set_column(0,4,30)
        sheet.set_row(0,40)
        sheet.set_row(1,30)
        sheet.set_row(2,30)
        
        # Write the report title
        sheet.merge_range('A1:E1', 'Delivery Detail', header_format)
        sheet.merge_range('A2:E2', f'From {lines.tr_date} To {lines.rc_date}',label_format)
        
        # Write column headers
        headers = ['Reference', 'Contact', 'Delivery Type', 'Company', 'Status']
        for col_num, header in enumerate(headers):
            sheet.write(2, col_num, header, label_format)
        
        row = 3
        for v in lines.picking_record:
            sheet.set_row(row,20)
            sheet.write(row,0,v.name,line_format)
            partner = v.partner_id.name if v.partner_id else ''
            sheet.write(row,1,partner,line_format)
            type = v.type.name if v.type else ''
            sheet.write(row,2,type,line_format)
            sheet.write(row,3,v.company_id.name,line_format)
            sheet.write(row,4,v.state,line_format)
            
            row +=1
