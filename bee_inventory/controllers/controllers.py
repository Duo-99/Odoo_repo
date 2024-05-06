# -*- coding: utf-8 -*-
# from odoo import http


# class BeeInventory(http.Controller):
#     @http.route('/bee_inventory/bee_inventory', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bee_inventory/bee_inventory/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('bee_inventory.listing', {
#             'root': '/bee_inventory/bee_inventory',
#             'objects': http.request.env['bee_inventory.bee_inventory'].search([]),
#         })

#     @http.route('/bee_inventory/bee_inventory/objects/<model("bee_inventory.bee_inventory"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bee_inventory.object', {
#             'object': obj
#         })
