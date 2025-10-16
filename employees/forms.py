from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employee, Department

# class UserRegistrationForm(UserCreationForm):
#     full_name = forms.CharField(max_length=100, required=True)
#     email = forms.EmailField(required=True)
#     employee_id = forms.CharField(max_length=20, required=True)

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    employee_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter employee ID'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'employee_id', 'department', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("This employee ID is already taken.")
        return employee_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        
        # Split full name
        name_parts = self.cleaned_data['full_name'].split()
        user.first_name = name_parts[0]
        user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        if commit:
            user.save()
            # Create employee profile
            Employee.objects.create(
                user=user,
                employee_id=self.cleaned_data['employee_id'],
                department=self.cleaned_data['department']
            )
        
        return user

class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'department', 'phone', 'address', 'profile_picture']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Your address'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        # Check if employee_id is already taken by another user
        if Employee.objects.filter(employee_id=employee_id).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This employee ID is already taken.")
        return employee_id

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already registered.")
        return email