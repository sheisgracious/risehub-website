from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Course, Cohort, Webinar, InterestForm as InterestFormModel,
    Enrollment, StudentProfile
)
from .forms import (
    InterestFormSubmission, ContactForm, WebinarRegistrationForm,
    StudentRegistrationForm, StudentProfileForm, EnrollmentForm
)


def home(request):
    """Homepage view"""
    # Get active course and upcoming cohorts
    active_courses = Course.objects.filter(is_active=True)
    upcoming_cohorts = Cohort.objects.filter(
        status__in=['recruiting', 'planning']
    ).order_by('start_date')[:3]
    
    # Get upcoming webinars
    from django.utils import timezone
    upcoming_webinars = Webinar.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')[:2]
    
    context = {
        'courses': active_courses,
        'cohorts': upcoming_cohorts,
        'webinars': upcoming_webinars,
    }
    return render(request, 'info_site/home.html', context)


def about_view(request):
    """About us page"""
    return render(request, 'info_site/about.html', {'page_title': 'About Us'})

def facilitators_view(request):
    return render(request, 'info_site/facilitators.html')

# def interest_form_view(request):
#     """Handle interest/enrollment form"""
#     if request.method == 'POST':
#         form = InterestFormSubmission(request.POST)
#         if form.is_valid():
#             interest = form.save()
            
#             # Send confirmation email to student
#             try:
#                 send_mail(
#                     subject='Thank You for Your Interest in Rise Hub!',
#                     message=f'''
#                     Dear {interest.full_name},
                    
#                     Thank you for your interest in {interest.interested_course.title}!
                    
#                     Our team will contact you within 24-48 hours to schedule your free 
#                     technology assessment call and answer any questions you may have.
                    
#                     We're excited to help you on your digital learning journey!
                    
#                     Best regards,
#                     The Rise Hub Team
                    
#                     Contact: info@risehub.site
#                     ''',
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[interest.email],
#                     fail_silently=True,
#                 )
#             except Exception as e:
#                 # Log error but don't fail the submission
#                 print(f"Email error: {e}")
            
#             messages.success(
#                 request,
#                 'Thank you! We\'ve received your interest form. '
#                 'Our team will contact you within 24-48 hours to schedule '
#                 'your free technology assessment call.'
#             )
#             return redirect('home')
#     else:
#         form = InterestFormSubmission()
    
#     context = {
#         'form': form,
#         'page_title': 'Express Your Interest',
#     }
#     return render(request, 'info_site/interest_form.html', context)


def contact_view(request):
    """Handle contact form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            messages.success(
                request,
                'Thank you for contacting us! We\'ll respond to your message shortly.'
            )
            return redirect('home')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'page_title': 'Contact Us',
    }
    return render(request, 'info_site/contact.html', context)


def webinar_registration_view(request, webinar_id):
    """Handle webinar registration"""
    webinar = get_object_or_404(Webinar, id=webinar_id, is_active=True)
    
    if request.method == 'POST':
        form = WebinarRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.webinar = webinar
            
            # Check if already registered
            if WebinarRegistration.objects.filter(
                webinar=webinar, 
                email=registration.email
            ).exists():
                messages.warning(
                    request,
                    'You are already registered for this webinar. Check your email for the Zoom link.'
                )
                return redirect('webinar_list')
            
            # Check if webinar is full
            if webinar.spots_remaining <= 0:
                messages.error(
                    request,
                    'Sorry, this webinar is fully booked. Please check for other upcoming webinars.'
                )
                return redirect('webinar_list')
            
            registration.save()
            
            # Send confirmation email with Zoom link
            try:
                send_mail(
                    subject=f'Confirmed: {webinar.title}',
                    message=f'''
                    Dear {registration.full_name},
                    
                    You're confirmed for our free webinar!
                    
                    Webinar: {webinar.title}
                    Date & Time: {webinar.date.strftime('%B %d, %Y at %I:%M %p')}
                    Duration: {webinar.duration_minutes} minutes
                    
                    Zoom Link: {webinar.zoom_link}
                    
                    We'll send a reminder 24 hours before the webinar.
                    
                    Looking forward to seeing you there!
                    
                    Best regards,
                    The Rise Hub Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[registration.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {e}")
            
            messages.success(
                request,
                f'You\'re registered for {webinar.title}! Check your email for the Zoom link.'
            )
            return redirect('webinar_list')
    else:
        form = WebinarRegistrationForm()
    
    context = {
        'form': form,
        'webinar': webinar,
        'page_title': f'Register for {webinar.title}',
    }
    return render(request, 'info_site/webinar_registration.html', context)


def webinar_list_view(request):
    """List all upcoming webinars"""
    from django.utils import timezone
    
    upcoming_webinars = Webinar.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')
    
    context = {
        'webinars': upcoming_webinars,
        'page_title': 'Free Webinars',
    }
    return render(request, 'info_site/webinar_list.html', context)


def course_detail_view(request, course_id):
    """Detailed view of a course"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    curriculum = course.curriculum.all().order_by('week_number')
    upcoming_cohorts = course.cohorts.filter(
        status__in=['recruiting', 'planning']
    ).order_by('start_date')
    
    context = {
        'course': course,
        'curriculum': curriculum,
        'cohorts': upcoming_cohorts,
        'page_title': course.title,
    }
    return render(request, 'info_site/course_detail.html', context)


# Student Portal Views
def student_registration_view(request):
    """Student account registration"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Welcome to Rise Hub! Please complete your profile to enroll in courses.'
            )
            return redirect('student_profile')
    else:
        form = StudentRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Create Student Account',
    }
    return render(request, 'info_site/student_registration.html', context)


@login_required
def student_profile_view(request):
    """View and edit student profile"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = StudentProfile.objects.create(
            user=request.user,
            phone_number=''
        )
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'page_title': 'My Profile',
    }
    return render(request, 'info_site/student_profile.html', context)


@login_required
def student_dashboard_view(request):
    """Student dashboard - shows enrollments and progress"""
    enrollments = request.user.enrollments.all().order_by('-enrolled_at')
    
    context = {
        'enrollments': enrollments,
        'page_title': 'My Dashboard',
    }
    return render(request, 'info_site/student_dashboard.html', context)


@login_required
def enrollment_view(request):
    """Enroll in a cohort"""
    # Check if profile is complete
    try:
        profile = request.user.student_profile
        if not profile.phone_number:
            messages.warning(
                request,
                'Please complete your profile before enrolling.'
            )
            return redirect('student_profile')
    except StudentProfile.DoesNotExist:
        messages.warning(
            request,
            'Please complete your profile before enrolling.'
        )
        return redirect('student_profile')
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            cohort = form.cleaned_data['cohort']
            
            # Check if already enrolled
            if Enrollment.objects.filter(
                student=request.user,
                cohort=cohort
            ).exists():
                messages.warning(
                    request,
                    'You are already enrolled in this cohort.'
                )
                return redirect('student_dashboard')
            
            # Check if cohort is full
            if cohort.spots_remaining <= 0:
                messages.error(
                    request,
                    'Sorry, this cohort is full. Please select another start date.'
                )
                return redirect('enrollment')
            
            # Create enrollment
            enrollment = Enrollment.objects.create(
                student=request.user,
                cohort=cohort,
                status='pending'
            )
            
            messages.success(
                request,
                f'You\'ve been enrolled in {cohort.name}! '
                f'Please proceed to payment (GHS {cohort.course.price}). '
                f'We\'ll contact you within 24 hours to schedule your assessment call.'
            )
            return redirect('enrollment_payment', enrollment_id=enrollment.id)
    else:
        form = EnrollmentForm()
    
    context = {
        'form': form,
        'page_title': 'Enroll in Course',
    }
    return render(request, 'info_site/enrollment.html', context)


@login_required
def enrollment_payment_view(request, enrollment_id):
    """Payment page for enrollment"""
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        student=request.user
    )
    
    if request.method == 'POST':
        # Here you would integrate with a payment gateway
        # For now, we'll just mark as pending payment
        payment_method = request.POST.get('payment_method')
        
        messages.success(
            request,
            'Payment information received! Our team will contact you to confirm payment. '
            'Once payment is confirmed, you\'ll receive your assessment call schedule.'
        )
        return redirect('student_dashboard')
    
    context = {
        'enrollment': enrollment,
        'cohort': enrollment.cohort,
        'course': enrollment.cohort.course,
        'page_title': 'Complete Payment',
    }
    return render(request, 'info_site/enrollment_payment.html', context)


@login_required
def cohort_materials_view(request, cohort_id):
    """View course materials for enrolled cohort"""
    cohort = get_object_or_404(Cohort, id=cohort_id)
    
    # Check if student is enrolled
    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        cohort=cohort,
        status__in=['enrolled', 'completed']
    )
    
    curriculum = cohort.course.curriculum.all().order_by('week_number')
    assignments = cohort.assignments.all().order_by('week_number')
    
    context = {
        'cohort': cohort,
        'enrollment': enrollment,
        'curriculum': curriculum,
        'assignments': assignments,
        'page_title': f'{cohort.name} - Materials',
    }
    return render(request, 'info_site/cohort_materials.html', context)