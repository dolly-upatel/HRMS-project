import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models import Department

def create_departments():
    departments = [
        ('HR', 'Human Resources Department'),
        ('IT', 'Information Technology Department'),
        ('Finance', 'Finance Department'),
        ('Marketing', 'Marketing Department'),
        ('Operations', 'Operations Department'),
        ('R&D', 'Research & Development Department'),
        ('Sales', 'Sales Department'),
        ('Support', 'Customer Support Department'),
    ]
    
    print("Creating departments...")
    for code, desc in departments:
        dept, created = Department.objects.get_or_create(
            name=code,
            defaults={'description': desc}
        )
        if created:
            print(f"✅ Created: {dept.name}")
        else:
            print(f"📁 Exists: {dept.name}")
    
    print(f"Total departments: {Department.objects.count()}")

if __name__ == '__main__':
    create_departments()