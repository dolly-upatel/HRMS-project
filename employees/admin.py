from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Employee, Department, Attendance

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employee'

class CustomUserAdmin(UserAdmin):
    inlines = (EmployeeInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_employee_id', 'get_department', 'is_staff')
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id
    get_employee_id.short_description = 'Employee ID'
    
    def get_department(self, obj):
        return obj.employee.department
    get_department.short_description = 'Department'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    list_filter = ('date', 'status', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    date_hierarchy = 'date'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)