from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    InterestForm, ContactMessage, WebinarRegistration, 
    StudentProfile, Enrollment
)


class InterestFormSubmission(forms.ModelForm):
    """Form for students to express interest in a course"""
    
    class Meta:
        model = InterestForm
        fields = [
            'full_name', 'email', 'phone_number', 'age',
            'interested_course', 'preferred_cohort',
            'how_did_you_hear', 'message'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+233 XXX XXX XXX'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your age (optional)',
                'min': '1'
            }),
            'interested_course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'preferred_cohort': forms.Select(attrs={
                'class': 'form-control'
            }),
            'how_did_you_hear': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Any questions or special requirements? (optional)'
            }),
        }
        labels = {
            'full_name': 'Full Name *',
            'email': 'Email Address *',
            'phone_number': 'Phone Number *',
            'age': 'Age (optional)',
            'interested_course': 'Which course interests you? *',
            'preferred_cohort': 'Preferred start date (if available)',
            'how_did_you_hear': 'How did you hear about us?',
            'message': 'Questions or Comments',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make preferred_cohort optional
        self.fields['preferred_cohort'].required = False
        self.fields['age'].required = False
        self.fields['how_did_you_hear'].required = False
        self.fields['message'].required = False


class ContactForm(forms.ModelForm):
    """General contact/question form"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+233 XXX XXX XXX (optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What is your question about?'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your message...'
            }),
        }
        labels = {
            'name': 'Name *',
            'email': 'Email Address *',
            'phone': 'Phone Number',
            'subject': 'Subject *',
            'message': 'Message *',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False


class WebinarRegistrationForm(forms.ModelForm):
    """Form for registering for free webinars"""
    
    class Meta:
        model = WebinarRegistration
        fields = ['full_name', 'email', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+233 XXX XXX XXX'
            }),
        }
        labels = {
            'full_name': 'Full Name *',
            'email': 'Email Address *',
            'phone': 'Phone Number *',
        }


class StudentRegistrationForm(UserCreationForm):
    """Extended user registration form for students"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+233 XXX XXX XXX'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes to all fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create student profile
            StudentProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number']
            )
        return user


class StudentProfileForm(forms.ModelForm):
    """Form for completing/updating student profile"""
    
    class Meta:
        model = StudentProfile
        fields = [
            'phone_number', 'date_of_birth', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'tech_skill_level', 'owns_smartphone', 'owns_computer',
            'device_type', 'preferred_contact'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+233 XXX XXX XXX'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'tech_skill_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'owns_smartphone': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'owns_computer': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'device_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., iPhone 12, Samsung Galaxy Tab'
            }),
            'preferred_contact': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'phone_number': 'Phone Number *',
            'date_of_birth': 'Date of Birth',
            'address': 'Address',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
            'tech_skill_level': 'Current Technology Skill Level *',
            'owns_smartphone': 'I own a smartphone',
            'owns_computer': 'I own a computer/laptop',
            'device_type': 'Device Type/Model',
            'preferred_contact': 'Preferred Contact Method *',
        }


class EnrollmentForm(forms.ModelForm):
    """Form for enrolling in a specific cohort"""
    agree_to_terms = forms.BooleanField(
        required=True,
        label="I agree to the course terms and payment policy"
    )
    
    class Meta:
        model = Enrollment
        fields = ['cohort']
        widgets = {
            'cohort': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'cohort': 'Select Course Start Date *'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active cohorts that are recruiting
        from .models import Cohort
        if isinstance(self.fields['cohort'], forms.ModelChoiceField):
            self.fields['cohort'].queryset = Cohort.objects.filter(
                status__in=['recruiting', 'planning']
            ).order_by('start_date')