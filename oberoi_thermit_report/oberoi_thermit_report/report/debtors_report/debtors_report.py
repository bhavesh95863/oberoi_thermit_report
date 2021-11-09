# Copyright (c) 2013, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt,cstr
from erpnext.stock.utils import get_stock_balance


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters=None):
	return [
		{
			"label": _("Sales Order"),
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 150
		},
		{
			"label": _("Customer Group"),
			"fieldname": "customer_group",
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": 200
		},
		{
			"label": _("Business Line"),
			"fieldname": "business_line",
			"fieldtype": "Data"
		},
		{
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Warehouse Details"),
			"fieldname": "warehouse_details",
			"fieldtype": "Link",
			"options":"Warehouse",
			"width": 150
		},
		{
			"label": _("Warehouse Value"),
			"fieldname": "warehouse_value",
			"fieldtype": "HTML",
			"width": 150
		},
		{
			"label": _("PI Details"),
			"fieldname": "pi_details",
			"fieldtype": "Link",
			"options":"Proforma Invoice",
			"width": 250
		},
		{
			"label": _("Total PI Amount"),
			"fieldname": "total_pi_amount",
			"fieldtype": "Currency"
		},
		{
			"label": _("SI Details"),
			"fieldname": "si_details",
			"fieldtype": "Link",
			"options":"Sales Invoice"
		},
		{
			"label": _("Total SI Amount"),
			"fieldname": "total_si_amount",
			"fieldtype": "Currency"
		},
		{
			"label": _("Total PI receivables"),
			"fieldname": "total_pi_receivables",
			"fieldtype": "Currency"
		},
		{
			"label": _("Total SI receivables"),
			"fieldname": "total_si_receivables",
			"fieldtype": "Currency"
		},
		{
			"label": _("Total Receivables (Claimed)"),
			"fieldname": "total_receivables_claimed",
			"fieldtype": "Currency"
		},
		{
			"label": _("Total Receivables (Including Unclaimed)"),
			"fieldname": "total_receivables_unclaimed",
			"fieldtype": "Currency"
		},
		{
			"label": _("Balance to Claim"),
			"fieldname": "balance_to_claim",
			"fieldtype": "Currency"
		},
		{
			"label": _("Total Payment Received"),
			"fieldname": "total_payment_received",
			"fieldtype": "Currency"
		},
		{
			"label": _("Balance To Receive As Per Payment Terms"),
			"fieldname": "balance_to_receive",
			"fieldtype": "Currency"
		},
		{
			"label": _("Actual Balance to Receive (Incl Unclaimed)"),
			"fieldname": "actual_balance_to_receive",
			"fieldtype": "Currency"
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"hidden":1
		}

	
	]


def get_data(filters):
	conditions = get_conditions(filters)
	sales_order_data = frappe.db.sql("""SELECT so.name AS 'sales_order',
       so.customer_group AS 'customer_group',
       so.business_line AS 'business_line',
       so.customer_name AS 'customer_name',
       'Click Here' AS 'warehouse_details',
       '' AS 'amount',
       'Click Here' AS 'pi_details',

  (SELECT sum(grand_total_to_pay_now)
   FROM `tabProforma Invoice`
   WHERE docstatus=1
     AND sales_order=so.name) AS 'total_pi_amount',
       'Click Here' AS 'si_details',

  (SELECT sum(grand_total)
   FROM `tabSales Invoice`
   WHERE docstatus=1
     AND sales_order=so.name) AS 'total_si_amount',
       '' AS 'total_pi_receivable',
       '' AS 'total_si_receivable',
       '' AS 'total_receivable_claimed',
       '' AS 'total_receivable_unclaimed',
       '' AS 'balance_to_claim',
       '' AS 'total_payment_received',
       '' AS 'balance_to_receive_as_per_terms',
       '' AS 'actual_balance_to_receive',

  (SELECT name
   FROM `tabWarehouse`
   WHERE sales_order=so.name
   LIMIT 1) AS 'warehouse'
FROM `tabSales Order` AS so
WHERE so.docstatus<>2 %s""" % conditions,filters,as_list=1)
	get_other_details(sales_order_data)
	return filter_final_data(filters,sales_order_data)


def filter_final_data(filters,order_data):
	'''apply additional filters'''
	data = []
	for order in order_data:
		if filters.get('actual_balnace_not_equal_zero'):
			if flt(order[16]) == 0 and flt(order[17]) == 0:
				continue
		if filters.get('actual_balnace_greater_than_zero'):
			if flt(order[16]) <= 0 and flt(order[17]) <= 0:
				continue
		data.append(order)
	return data

def get_conditions(filters):
	conditions = ""

	if filters.get("customer"):
		conditions += "and so.customer = %(customer)s"
	if filters.get("business_line"):
		conditions += "and so.business_line = %(business_line)s"
	if filters.get("sales_order"):
		conditions += " and so.name = %(sales_order)s"
	if filters.get("customer_group"):
		conditions += " and so.customer_group = %(customer_group)s"
	if filters.get("item"):
		conditions += " and soi.item_code = %(item)s"
	return conditions

def get_other_details(order_data):
	for order in order_data:
		items = frappe.get_doc("Sales Order",order[0]).items
		warehouse_balance = get_warehouse_balance_qty(order[0],items)
		order[5] = warehouse_balance

		if flt(order[7],0) > 0:
			order[10] = order[7] - flt(order[9],0) #Total PI receivables
		else:
			order[10] = 0 #Total PI receivables
		order[11] = order[9]  #Total SI receivables
		order[12] = flt(order[10],0) + flt(order[11],0) #Total Receivables (Claimed)
		order[13] = flt(order[9],0) + warehouse_balance #Total Receivables (Including Unclaimed)
		order[14] = flt(order[13],0) - flt(order[12],0) #Balance to Claim
		order[15] = get_payment_details(order) #Total Payment Received
		if order[15]:
			order[16] = order[12] - order[15] #Balance To receive As per Payment Terms
			order[17] = order[13] - order[15] #Actual Balance to Receive (Incl Unclaimed)
		else:
			order[16] = order[12] #Balance To receive As per Payment Terms
			order[17] = order[13] #Actual Balance to Receive (Incl Unclaimed)



def get_warehouse_balance_qty(order,items):
	'''get billing warehouse value which is linked with sales order'''

	warehouses = frappe.db.sql("""SELECT name
FROM `tabWarehouse`
WHERE sales_order=%s
  AND is_group=0""",order,as_dict=1)

	total_balance_value = 0
	if len(warehouses) >= 1:
		for item in items:
			if item.rate > 0:
				for warehouse in warehouses:
					total_balance_value += flt(get_stock_balance(item.item_code,warehouse.name)) * item.rate
	return total_balance_value
	

def get_payment_details(order):
	order_data = frappe.db.sql("""SELECT sum(p.paid_amount+
             (SELECT sum(amount)
              FROM `tabPayment Entry Deduction`
              WHERE parent=p.name)+p.sd_amount+p.sd_amount_1_percent) AS 'payment_amount'
FROM `tabPayment Entry` AS p
WHERE p.sales_order=%s
  AND p.docstatus=1
  AND p.payment_type='Receive'""",order[0],as_dict=1)
	if len(order_data) >= 1:
		return order_data[0].payment_amount
	else:
		return 0