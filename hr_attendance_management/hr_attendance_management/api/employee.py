import frappe
from frappe import _

@frappe.whitelist()
def get_employees_by_branch(branch=None):
    """Return list of employees filtered by branch"""
    if not branch:
        frappe.throw(_("Branch is required"), frappe.MandatoryError)

    employees = frappe.get_all(
        "Employee",
        filters={"branch": branch},
        fields=["name", "employee_name", "designation", "department", "status"]
    )

    return employees