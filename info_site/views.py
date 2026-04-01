from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Course, Cohort, Webinar, WebinarRegistration,
    InterestForm as InterestFormModel,
    Enrollment, StudentProfile
)
from .forms import (
    InterestFormSubmission, ContactForm, WebinarRegistrationForm,
    StudentRegistrationForm, StudentProfileForm, EnrollmentForm
)


def home(request):
    active_courses = Course.objects.filter(is_active=True)
    upcoming_cohorts = Cohort.objects.filter(
        status__in=['recruiting', 'planning']
    ).order_by('start_date')[:3]

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
    return render(request, 'info_site/about.html', {'page_title': 'About Us'})


def facilitators_view(request):
    return render(request, 'info_site/facilitators.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # FIX: was sending to info@rophejewels.com
            try:
                send_mail(
                    subject=f'New Contact Form: {contact.subject}',
                    message=f'''
New contact form submission from Rise Hub:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone or 'Not provided'}
Subject: {contact.subject}

Message:
{contact.message}

---
Submitted at: {contact.created_at.strftime('%B %d, %Y at %I:%M %p')}
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )

                send_mail(
                    subject='Thank you for contacting Rise Hub',
                    message=f'''
Dear {contact.name},

Thank you for reaching out to Rise Hub! We've received your message about "{contact.subject}".

Our team will review your inquiry and get back to you within 24-48 hours.

Best regards,
The Rise Hub Team

---
Contact us at info@risehub.site for any questions.
                    ''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[contact.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {e}")

            messages.success(
                request,
                "Thank you for contacting us! We'll respond to your message shortly."
            )
            return redirect('home')
    else:
        form = ContactForm()

    context = {
        'form': form,
        'page_title': 'Contact Us',
    }
    return render(request, 'info_site/contact.html', context)


def webinar_list_view(request):
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


def webinar_registration_view(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id, is_active=True)

    if request.method == 'POST':
        form = WebinarRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.webinar = webinar

            # FIX: WebinarRegistration was not imported before
            if WebinarRegistration.objects.filter(
                webinar=webinar,
                email=registration.email
            ).exists():
                messages.warning(
                    request,
                    'You are already registered for this webinar. Check your email for the Zoom link.'
                )
                return redirect('webinar_list')

            if webinar.spots_remaining <= 0:
                messages.error(
                    request,
                    'Sorry, this webinar is fully booked. Please check for other upcoming webinars.'
                )
                return redirect('webinar_list')

            registration.save()

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
                f"You're registered for {webinar.title}! Check your email for the Zoom link."
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


def course_syllabus_view(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    # FIX: was using 'curriculum' — correct related name is 'curriculum_weeks'
    curriculum = course.curriculum_weeks.all().order_by('week_number')

    context = {
        'course': course,
        'curriculum': curriculum,
        'page_title': course.title,
    }
    return render(request, 'info_site/course_syllabus.html', context)


def student_registration_view(request):
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


def page_not_found(request, exception=None):
    return render(request, 'info_site/404.html', status=404)


def server_error(request, exception=None):
    return render(request, 'info_site/500.html', status=500)


def access_forbidden(request, exception=None):
    return render(request, 'info_site/403.html', status=403)


@login_required
def student_profile_view(request):
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
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
    enrollments = request.user.enrollments.all().order_by('-enrolled_at')

    context = {
        'enrollments': enrollments,
        'page_title': 'My Dashboard',
    }
    return render(request, 'info_site/student_dashboard.html', context)


@login_required
def enrollment_view(request):
    try:
        profile = request.user.student_profile
        if not profile.phone_number:
            messages.warning(request, 'Please complete your profile before enrolling.')
            return redirect('student_profile')
    except StudentProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile before enrolling.')
        return redirect('student_profile')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            cohort = form.cleaned_data['cohort']

            if Enrollment.objects.filter(student=request.user, cohort=cohort).exists():
                messages.warning(request, 'You are already enrolled in this cohort.')
                return redirect('student_dashboard')

            if cohort.spots_remaining <= 0:
                messages.error(request, 'Sorry, this cohort is full. Please select another start date.')
                return redirect('enrollment')

            enrollment = Enrollment.objects.create(
                student=request.user,
                cohort=cohort,
                status='pending'
            )

            messages.success(
                request,
                f"You've been enrolled in {cohort.name}! "
                f"We'll contact you within 24 hours to schedule your assessment call."
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
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)

    if request.method == 'POST':
        messages.success(
            request,
            "Payment information received! Our team will contact you to confirm payment."
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
    cohort = get_object_or_404(Cohort, id=cohort_id)

    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        cohort=cohort,
        status__in=['enrolled', 'completed']
    )

    # FIX: was using cohort.course.curriculum — correct related name is curriculum_weeks
    curriculum = cohort.course.curriculum_weeks.all().order_by('week_number')
    assignments = cohort.assignments.all().order_by('week_number')

    context = {
        'cohort': cohort,
        'enrollment': enrollment,
        'curriculum': curriculum,
        'assignments': assignments,
        'page_title': f'{cohort.name} - Materials',
    }
    return render(request, 'info_site/cohort_materials.html', context)