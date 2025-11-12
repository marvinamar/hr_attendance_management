import frappe
import json
from frappe import _

@frappe.whitelist()
def get_employees_by_branch(branch=None):
    """
    Return list of employees filtered by branch
    Includes full URLs for images and custom fields.
    """
    try:
        base_url = frappe.utils.get_url()

        if not branch:
            frappe.throw(_("Branch is required"), frappe.MandatoryError)

        employees = frappe.get_all(
            "Employee",
            filters={"branch": branch},
            fields=[
                "name",
                "employee_name",
                "branch",
                "image",
                "first_name",
                "middle_name",
                "last_name",
                "gender",
                "date_of_birth",
                "user_id",
                "company",
                "custom_embedding",
                "custom_biometric_image"
            ]
        )

        # Convert image paths to full URLs
        for emp in employees:
            if emp.get("image") and not emp["image"].startswith("http"):
                emp["image"] = f"{base_url}{emp['image']}"
            if emp.get("custom_biometric_image") and not emp["custom_biometric_image"].startswith("http"):
                emp["custom_biometric_image"] = f"{base_url}{emp['custom_biometric_image']}"

        # Build response
        if employees:
            frappe.response["message"] = f"Success: {len(employees)} employee(s) found for branch '{branch}'"
        else:
            frappe.response["message"] = f"No employees found for branch '{branch}'"

        frappe.response["data"] = employees

    except Exception as e:
        # Return exact error in response
        frappe.response["message"] = f"Error: {str(e)}"
        frappe.response["data"] = []
    
@frappe.whitelist()
def update_eployee_api(name=None,custom_embedding=None,custom_biometric_image=None):
    try:
        if not name:
            frappe.throw(_("Name is required"), frappe.MandatoryError)

        employee = frappe.get_doc("Employee", name)
        
        employee.custom_embedding = custom_embedding
        employee.custom_biometric_image = custom_biometric_image

        # Save the changes
        employee.save(ignore_permissions=True)

        frappe.response["message"] = f"Employee '{name}' updated successfully."

    except Exception as e:
        # Return exact error in response
        frappe.response["message"] = f"Error: {str(e)}"


@frappe.whitelist(allow_guest=True)
def employee_attendance(
    employee=None,
    time=None,
    log_type=None,
    device_id=None,
    latitude=None,
    longitude=None
):
    import json

    try:
        # 🔹 Try to parse JSON if employee not passed as argument
        if not employee and frappe.request and frappe.request.data:
            try:
                data = json.loads(frappe.request.data)
                employee = data.get("employee")
                time = data.get("time")
                log_type = data.get("log_type")
                device_id = data.get("device_id")
                latitude = data.get("latitude")
                longitude = data.get("longitude")
            except Exception as err:
                frappe.log_error(f"JSON parse error: {err}", "Employee Attendance API")

        # 🔹 Validate required fields
        if not employee:
            frappe.throw(_("Employee is required"), frappe.MandatoryError)

        # 🔹 Create attendance record
        attendance = frappe.new_doc("Employee Checkin")
        attendance.employee = employee
        attendance.time = time
        attendance.log_type = log_type
        attendance.device_id = device_id
        attendance.latitude = latitude
        attendance.longitude = longitude

        attendance.insert(ignore_permissions=True)
        attendance.submit()
        frappe.db.commit()

        frappe.response["status"] = "success"
        frappe.response["message"] = "Attendance saved successfully"
        frappe.response["attendance_id"] = attendance.name

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Employee Attendance Error")
        frappe.response["status"] = "error"
        frappe.response["message"] = f"Error: {str(e)}"



# @frappe.whitelist()
# def employee_attendance(
#     employee=None,
#     time=None,
#     log_type=None,
#     device_id=None,
#     latitude=None,
#     longitude=None
# ):
#     try:        

#         if not employee:
#             frappe.throw(_("Employee is required"), frappe.MandatoryError)
        
#         attendance = frappe.new_doc("Employee Checkin")
#         attendance.employee = employee
#         attendance.time = time
#         attendance.log_type = log_type
#         attendance.device_id = device_id
#         attendance.latitude = latitude
#         attendance.longitude = longitude

#         # Insert and submit record
#         attendance.insert(ignore_permissions=True)
#         attendance.submit()
#         frappe.db.commit()

#         frappe.response["status"] = "success"
#         frappe.response["message"] = "Attendance saved successfully"
#         frappe.response["attendance_id"] = attendance.name

#     except Exception as e:
#         # Return exact error in response
#         frappe.response["message"] = f"Error: {str(e)}"
