# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Microfinance Servicing Portal Page."""

import frappe
from frappe import _
from frappe.utils import nowdate


def get_context(context):
    """Get context for microfinance servicing portal."""
    context.no_cache = 1
    context.user = frappe.session.user
    customer = get_customer_info(context.user)
    context.customer = customer
    context.stats = get_portal_statistics(customer)
    context.loans = get_customer_loans(customer)
    context.invoices = get_customer_invoices(customer)
    return context


def get_customer_info(user):
    """Get customer information for the user."""
    customer = frappe.db.get_value(
        "Customer",
        {"email_id": user},
        ["name", "customer_name", "territory", "customer_group"],
    )
    if not customer:
        return None
    return {
        "name": customer[0],
        "customer_name": customer[1],
        "territory": customer[2],
        "customer_group": customer[3],
    }


def get_portal_statistics(customer):
    """Get portal statistics for the customer."""
    if not customer:
        return {}
    return {
        "active_loans": frappe.db.count("Microfinance Loan", {"customer": customer["name"], "status": "Active"}),
        "pending_loans": frappe.db.count("Microfinance Loan", {"customer": customer["name"], "status": "Pending"}),
        "completed_loans": frappe.db.count("Microfinance Loan", {"customer": customer["name"], "status": ["in", ["Paid", "Completed"]]}),
        "total_invoices": frappe.db.count("Sales Invoice", {"customer": customer["name"], "docstatus": 1}),
        "pending_invoices": frappe.db.count("Sales Invoice", {"customer": customer["name"], "status": "Overdue"}),
    }


def get_customer_loans(customer, limit=10):
    """Get loans for the customer."""
    if not customer:
        return []
    return frappe.get_all(
        "Microfinance Loan",
        filters={"customer": customer["name"], "docstatus": ["<", 2]},
        fields=['name', 'loan_amount', 'interest_rate', 'status', 'disbursement_date'],
        order_by="disbursement_date desc",
        limit=limit,
    )


def get_customer_invoices(customer, limit=10):
    """Get recent invoices for the customer."""
    if not customer:
        return []
    return frappe.get_all(
        "Sales Invoice",
        filters={"customer": customer["name"], "docstatus": 1},
        fields=["name", "posting_date", "grand_total", "outstanding_amount", "status"],
        order_by="posting_date desc",
        limit=limit,
    )


@frappe.whitelist()
def get_loan_details(loan_name):
    """Get details for a specific Microfinance Loan."""
    try:
        doc = frappe.get_doc("Microfinance Loan", loan_name)
        data = {"success": True, "loan_name": doc.name}
        for field in ['loan_amount', 'interest_rate', 'repayment_period', 'monthly_payment', 'outstanding_amount', 'status']:
            data[field] = getattr(doc, field, None)
        return data
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def make_payment(loan_name, amount):
    """Make a payment for a Microfinance Loan."""
    try:
        customer = get_customer_info(frappe.session.user)
        if not customer:
            return {"success": False, "message": _("Customer not found")}
        payment = frappe.new_doc("Payment Entry")
        payment.payment_type = "Receive"
        payment.party_type = "Customer"
        payment.party = customer["name"]
        payment.paid_amount = amount
        payment.received_amount = amount
        payment.payment_date = nowdate()
        payment.append(
            "references",
            {
                "reference_doctype": "Microfinance Loan",
                "reference_name": loan_name,
                "allocated_amount": amount,
            },
        )
        payment.save()
        payment.submit()
        return {"success": True, "payment": payment.name}
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_loan_schedule(loan_name):
    """Get payment schedule for a Microfinance Loan."""
    try:
        schedule = frappe.get_all(
            "Microfinance Loan Repayment Schedule",
            filters={"parent": loan_name},
            fields=["payment_date", "principal_amount", "interest_amount", "total_amount", "status"],
            order_by="payment_date",
        )
        return {"success": True, "schedule": schedule}
    except Exception as e:
        return {"success": False, "message": str(e)}
