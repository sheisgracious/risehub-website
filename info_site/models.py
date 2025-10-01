from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

# Models for Course Management System
class Course(models.Model):
    """Main course offering - e.g., Digital Literacy 101"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_weeks = models.IntegerField(default=6)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='GHS')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


# Webinar Models - Move BEFORE WebinarRegistration references
class Webinar(models.Model):
    """Free introductory webinars"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    zoom_link = models.URLField()
    registration_limit = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def registration_count(self):
        return self.registrations.count()
    
    @property
    def spots_remaining(self):
        return max(0, self.registration_limit - self.registration_count)


class WebinarRegistration(models.Model):
    """Track webinar registrations"""
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='registrations')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    attended = models.BooleanField(default=False)
    enrolled_after = models.BooleanField(default=False)
    
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-registered_at']
        unique_together = ['webinar', 'email']
    
    def __str__(self):
        return f"{self.full_name} - {self.webinar.title}"


# Enrollment Models - Move BEFORE Cohort references
class Enrollment(models.Model):
    """Student enrollment in a specific cohort"""
    STATUS_CHOICES = [
        ('interested', 'Expressed Interest'),
        ('assessment_scheduled', 'Assessment Scheduled'),
        ('pending', 'Pending Payment'),
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('cancelled', 'Cancelled'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    cohort = models.ForeignKey('Cohort', on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='interested')
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Assessment call
    assessment_call_date = models.DateTimeField(null=True, blank=True)
    assessment_notes = models.TextField(blank=True)
    
    # Progress tracking
    attendance_count = models.IntegerField(default=0)
    assignments_completed = models.IntegerField(default=0)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-enrolled_at']
        unique_together = ['student', 'cohort']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.cohort.name}"
    
    @property
    def is_paid(self):
        return self.amount_paid >= self.cohort.course.price


class Cohort(models.Model):
    """A specific offering/session of a course"""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('recruiting', 'Recruiting'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='cohorts')
    name = models.CharField(max_length=100, help_text="e.g., Cohort 1 - January 2025")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    max_students = models.IntegerField(default=15)
    meeting_day = models.CharField(max_length=20, blank=True, help_text="e.g., Monday")
    meeting_time = models.TimeField(null=True, blank=True)
    zoom_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.course.title} - {self.name}"
    
    @property
    def current_enrollment_count(self):
        return self.enrollments.filter(status__in=['pending', 'enrolled']).count()
    
    @property
    def spots_remaining(self):
        return max(0, self.max_students - self.current_enrollment_count)


class WeekCurriculum(models.Model):
    """Weekly curriculum content for a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='curriculum_weeks')
    week_number = models.IntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=200)
    description = models.TextField()
    topics = models.TextField(help_text="One topic per line")
    learning_objectives = models.TextField(blank=True)
    materials_url = models.URLField(blank=True, help_text="Link to slides, resources")
    
    class Meta:
        ordering = ['course', 'week_number']
        unique_together = ['course', 'week_number']
    
    def __str__(self):
        return f"{self.course.title} - Week {self.week_number}: {self.title}"


# Student Enrollment Models
class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Technology assessment
    TECH_SKILL_LEVELS = [
        ('beginner', 'Complete Beginner'),
        ('basic', 'Basic Understanding'),
        ('intermediate', 'Intermediate'),
    ]
    
    tech_skill_level = models.CharField(
        max_length=20,
        choices=TECH_SKILL_LEVELS,
        default='beginner'
    )
    owns_smartphone = models.BooleanField(default=False)
    owns_computer = models.BooleanField(default=False)
    device_type = models.CharField(max_length=100, blank=True, help_text="e.g., iPhone, Samsung tablet")
    
    # Communication preferences
    CONTACT_PREFERENCES = [
        ('phone', 'Phone'), 
        ('email', 'Email'), 
        ('whatsapp', 'WhatsApp')
    ]
    
    preferred_contact = models.CharField(
        max_length=20,
        choices=CONTACT_PREFERENCES,
        default='phone'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Profile"


class InterestForm(models.Model):
    """Initial interest/lead capture form"""
    HOW_HEARD_CHOICES = [
        ('webinar', 'Free Webinar'),
        ('social_media', 'Social Media'),
        ('flyer', 'Flyer/Poster'),
        ('radio', 'Radio'),
        ('referral', 'Friend/Family Referral'),
        ('other', 'Other'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    age = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    
    # Interest details
    interested_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    preferred_cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True, blank=True)
    
    how_did_you_hear = models.CharField(
        max_length=100,
        choices=HOW_HEARD_CHOICES,
        blank=True
    )
    
    message = models.TextField(blank=True, help_text="Questions or special requests")
    
    # Status tracking
    contacted = models.BooleanField(default=False)
    converted_to_enrollment = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.created_at.strftime('%Y-%m-%d')}"


class ContactMessage(models.Model):
    """General contact/question form"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    is_responded = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


# Team/Instructor Models
class InstructorProfile(models.Model):
    """Profile for instructors/facilitators"""
    ROLE_CHOICES = [
        ('lead', 'Lead Instructor'),
        ('supporting', 'Supporting Facilitator'),
        ('admin', 'Admin/Operations'),
        ('marketing', 'Marketing Lead'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    university = models.CharField(max_length=200, blank=True)
    major = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    
    # Compensation
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


class CohortInstructor(models.Model):
    """Assignment of instructors to specific cohorts"""
    INSTRUCTOR_ROLES = [
        ('lead', 'Lead Instructor'), 
        ('supporting', 'Supporting Facilitator')
    ]
    
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='cohort_instructors')
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='cohort_assignments')
    role = models.CharField(
        max_length=20,
        choices=INSTRUCTOR_ROLES,
        default='supporting'
    )
    
    class Meta:
        unique_together = ['cohort', 'instructor']
    
    def __str__(self):
        return f"{self.instructor.user.get_full_name()} - {self.cohort.name} ({self.role})"


# Assignment and Progress Tracking
class Assignment(models.Model):
    """Weekly flashcard assignments"""
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='assignments')
    week_number = models.IntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=200)
    description = models.TextField()
    quizlet_url = models.URLField(blank=True)
    due_date = models.DateTimeField()
    
    class Meta:
        ordering = ['cohort', 'week_number']
        unique_together = ['cohort', 'week_number']
    
    def __str__(self):
        return f"{self.cohort.name} - Week {self.week_number}: {self.title}"


class AssignmentSubmission(models.Model):
    """Track student assignment completion"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    
    completed = models.BooleanField(default=False)
    score = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    notes = models.TextField(blank=True)
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.assignment.title}"