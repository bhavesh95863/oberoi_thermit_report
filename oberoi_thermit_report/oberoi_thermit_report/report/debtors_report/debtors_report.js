// Copyright (c) 2016, Bhavesh Maheshwari and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Debtors Report"] = {
	"filters": [
		{
			"fieldname":"sales_order",
			"label": __("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order"
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname":"business_line",
			"label": __("Business Line"),
			"fieldtype": "Select",
			"options": "\nATW\nTRANSLAMATIC\nGIRJ\nNON GIRJ\nRBM\nPOTAS\nFRACTURE DETECTION\nSCOUR MONITORING\nVEHICULAR USFD\nINSTRUMENTATION\n3rd PARTY AUDIT\nUSFD TESTING"
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"actual_balnace_not_equal_zero",
			"label": __("Claimed/Unclaimed Balance Not Zero"),
			"fieldtype": "Check"
		},
		{
			"fieldname":"actual_balnace_greater_than_zero",
			"label": __("Claimed/Unclaimed > 0"),
			"fieldtype": "Check"
		}

	],
	"formatter": function (value, row, column, data, default_formatter) {
		// console.log(data)
		if (column.fieldname == "warehouse_details" && data) {
			value = "Click Here";
			column.link_onclick = "frappe.query_reports['Debtors Report'].set_route_to_stock_balance(" + JSON.stringify(data) + ")";
		}
		if (column.fieldname == "pi_details" && data) {
			value = "Click Here";
			column.link_onclick = "frappe.query_reports['Debtors Report'].set_route_to_pi_list(" + JSON.stringify(data) + ")";	
		}
		if (column.fieldname == "si_details" && data) {
			value = "Click Here";
			column.link_onclick = "frappe.query_reports['Debtors Report'].set_route_to_si_list(" + JSON.stringify(data) + ")";	
		}
		value = default_formatter(value, row, column, data);
		return value;
	},
	"set_route_to_stock_balance": function (data) {
		if (data["warehouse"]) {
			frappe.route_options = {
				"warehouse": data["warehouse"]
			};
			// frappe.set_route("List", "Item");
			frappe.set_route("query-report", "Stock Balance");
		}else{
			frappe.msgprint("No Any Link Billing Warehouse Linked")
		}
	},
	"set_route_to_pi_list": function(data) {
		if(data["sales_order"]) {
			frappe.route_options = {
				"sales_order": data["sales_order"]
			};
			frappe.set_route("List", "Proforma Invoice");
		}
	},
	"set_route_to_si_list": function(data) {
		if(data["sales_order"]) {
			frappe.route_options = {
				"sales_order": data["sales_order"]
			};
			frappe.set_route("List", "Sales Invoice");
		}
	}
};
