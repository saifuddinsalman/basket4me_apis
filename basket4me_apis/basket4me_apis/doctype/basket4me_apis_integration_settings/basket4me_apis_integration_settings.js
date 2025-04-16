// Copyright (c) 2025, SaifUdDinSalman and contributors
// For license information, please see license.txt

frappe.ui.form.on("Basket4Me APIs Integration Settings", {
	refresh(frm) {
        add_btn_to_get_records(frm, 'Sales Order')
        add_btn_to_get_records(frm, 'Sales Invoice')
        add_btn_to_get_records(frm, 'Receipt')
	},
});

function add_btn_to_get_records(frm, doc_type) {
    let doc_wise_vars = {
        "Sales Order": {"doc":"Sales Order", "path": "sales_order_api_path", "date": "sales_order_access_date"},
        "Sales Invoice": {"doc":"Sales Invoice","path": "sales_invoice_api_path", "date": "sales_invoice_access_date"},
        "Receipt": {"doc":"Payment Entry","path": "receipts_api_path", "date": "receipts_access_date"},
    }
    if (!frm.doc[doc_wise_vars[doc_type]["path"]]) {
    frappe.msgprint(__(`Please set the API path for {doc_type}.`));
    return;}
    let date = frm.doc[doc_wise_vars[doc_type]["date"]]
    if (!date) {
        frappe.msgprint(__(`Please set the last access date for {doc_type}.`));
        return;}
    frm.add_custom_button(__(doc_type), () => {
        if (frm.is_dirty()) {
            frappe.msgprint(__('Please save the document first.'));
            return;
        }
        frappe.call({
            method: `basket4me_apis.main.make_api_call_background_job`,
            args:{"doctype": doc_wise_vars[doc_type]["doc"], "date": date},
            callback: function (r) {
                frappe.show_alert({
                    message: __('API call Job Started successfully.'),
                    indicator: 'green'
                });
                frm.reload_doc()
            }
        });
    }, __('Get Records'));
}
