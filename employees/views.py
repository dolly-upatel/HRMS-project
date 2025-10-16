from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from .models import Employee, Department, Attendance
from .forms import UserUpdateForm, EmployeeUpdateForm  

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        employee_id = request.POST.get('employee_id', '').strip()
        department_id = request.POST.get('department', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        print(f"Registration attempt - Name: {full_name}, Email: {email}, Employee ID: {employee_id}")  # Debug
        
        # Validation
        if not all([full_name, email, employee_id, department_id, password1, password2]):
            messages.error(request, "All fields are required.")
            return redirect('register')
        
        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return redirect('register')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')
        
        if Employee.objects.filter(employee_id=employee_id).exists():
            messages.error(request, "Employee ID already taken")
            return redirect('register')
        
        try:
            # Split full name
            name_parts = full_name.split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # Get department
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                # Create default department if not found
                department = Department.objects.first()
                if not department:
                    department = Department.objects.create(
                        name='General', 
                        description='General Department'
                    )
                messages.warning(request, "Selected department not found, assigned to General department")
            
            # Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            print(f"User created: {user.username}")  # Debug
            
            # Create employee profile
            employee = Employee.objects.create(
                user=user,
                employee_id=employee_id,
                department=department
            )
            
            print(f"Employee profile created: {employee.employee_id}")  # Debug
            
            # Auto login
            user = authenticate(username=email, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, "Registration successful! Welcome to the system.")
                return redirect('dashboard')
            else:
                messages.success(request, "Registration successful! Please login.")
                return redirect('login')
                
        except Exception as e:
            print(f"Registration error: {str(e)}")  # Debug
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('register')
    
    # GET request - show registration form
    # Get departments for the form
    departments = Department.objects.all()
    if not departments.exists():
        # Create some default departments
        default_departments = [
            ('HR', 'Human Resources'),
            ('IT', 'Information Technology'),
            ('Finance', 'Finance & Accounts'),
            ('Marketing', 'Marketing & Sales'),
            ('Operations', 'Operations'),
        ]
        
        for dept_name, dept_desc in default_departments:
            Department.objects.create(name=dept_name, description=dept_desc)
        
        departments = Department.objects.all()
        messages.info(request, "Default departments created")
    
    return render(request, 'register.html', {'departments': departments})
    
def custom_login(request):
    """Custom login view to handle authentication"""
    # Debug information
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        print("User already authenticated, redirecting to dashboard")
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password')
        
        print(f"Login attempt for: {username}")
        
        # Basic validation
        if not username or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, 'login.html')
        
        # Try to authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"Authentication successful for: {user.username}")
            
            # Check if employee profile exists, if not create one
            try:
                employee = user.employee
                print(f"Employee profile found: {employee.employee_id}")
            except Employee.DoesNotExist:
                print("Employee profile not found, creating...")
                # Create default department if none exists
                default_dept = Department.objects.first()
                if not default_dept:
                    default_dept = Department.objects.create(
                        name='General', 
                        description='General Department'
                    )
                
                # Create employee profile
                employee = Employee.objects.create(
                    user=user,
                    employee_id=f"EMP{user.id:03d}",
                    department=default_dept
                )
                print(f"Created employee profile: {employee.employee_id}")
            
            # Login the user
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name()}!")
            print(f"User logged in successfully, redirecting to dashboard")
            return redirect('dashboard')
        else:
            print("Authentication failed")
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')
    
    # GET request - show login form
    print("Showing login form")
    return render(request, 'login.html')

def custom_logout(request):
    """Custom logout view"""
    print(f"Logging out user: {request.user}")
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def dashboard(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        # Create employee profile if it doesn't exist
        default_dept = Department.objects.first()
        if not default_dept:
            default_dept = Department.objects.create(
                name='General', 
                description='General Department'
            )
        
        employee = Employee.objects.create(
            user=request.user,
            employee_id=f"EMP{request.user.id:03d}",
            department=default_dept
        )
    
    # Get today's date
    today = timezone.now().date()
    
    # Get today's attendance record
    today_attendance = Attendance.objects.filter(
        employee=employee, 
        date=today
    ).first()
    
    # Calculate attendance statistics
    all_attendance = Attendance.objects.filter(employee=employee)
    present_days = all_attendance.filter(status='PRESENT').count()
    absent_days = all_attendance.filter(status='ABSENT').count()
    
    # Get recent attendance (last 5 records)
    recent_attendance = all_attendance.order_by('-date', '-check_in')[:5]
    
    context = {
        'employee': employee,
        'present_days': present_days,
        'absent_days': absent_days,
        'today_attendance': today_attendance,
        'recent_attendance': recent_attendance,
        'current_date': today,
    }
    return render(request, 'dashboard.html', context)

@login_required
def mark_attendance(request):
    employee = request.user.employee
    today = timezone.now().date()
    now = timezone.now()
    
    # Get today's attendance record
    try:
        attendance = Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            status='PRESENT'
        )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'check_in' and not attendance.check_in:
            attendance.check_in = now.time()
            attendance.status = 'PRESENT'
            attendance.save()
            messages.success(request, f"Checked in successfully at {attendance.check_in.strftime('%H:%M %p')}")
            
        elif action == 'check_out' and attendance.check_in and not attendance.check_out:
            attendance.check_out = now.time()
            attendance.save()
            messages.success(request, f"Checked out successfully at {attendance.check_out.strftime('%H:%M %p')}")
            
        elif action == 'check_out' and not attendance.check_in:
            messages.error(request, "Please check in first before checking out")
        else:
            messages.info(request, "Attendance already marked for this action")
        
        return redirect('mark_attendance')
    
    context = {
        'attendance': attendance,
        'today': today,
        'now': now,
    }
    return render(request, 'mark_attendance.html', context)

@login_required
def attendance_history(request):
    employee = request.user.employee
    attendance_list = Attendance.objects.filter(employee=employee).order_by('-date')
    
    # Calculate summary statistics
    total_days = attendance_list.count()
    present_days = attendance_list.filter(status='PRESENT').count()
    absent_days = attendance_list.filter(status='ABSENT').count()
    late_days = attendance_list.filter(status='LATE').count()
    
    context = {
        'attendance_list': attendance_list,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
    }
    return render(request, 'attendance_history.html', context)

@login_required
def profile(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        # Create employee profile if it doesn't exist
        default_dept = Department.objects.first()
        if not default_dept:
            default_dept = Department.objects.create(
                name='General', 
                description='General Department'
            )
        
        employee = Employee.objects.create(
            user=request.user,
            employee_id=f"EMP{request.user.id:03d}",
            department=default_dept
        )
        messages.info(request, "Employee profile created successfully!")
    
    if request.method == 'POST':
        # Handle form submission
        user_form = UserUpdateForm(request.POST, instance=request.user)
        employee_form = EmployeeUpdateForm(request.POST, request.FILES, instance=employee)
        
        if user_form.is_valid() and employee_form.is_valid():
            user_form.save()
            employee_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            # Show form errors
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"User {field}: {error}")
            for field, errors in employee_form.errors.items():
                for error in errors:
                    messages.error(request, f"Employee {field}: {error}")
    else:
        # Initial form load
        user_form = UserUpdateForm(instance=request.user)
        employee_form = EmployeeUpdateForm(instance=employee)
    
    context = {
        'user_form': user_form,
        'employee_form': employee_form,
        'employee': employee
    }
    
    return render(request, 'profile.html', context)