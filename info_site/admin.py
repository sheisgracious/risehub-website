from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Course, Cohort, WeekCurriculum, StudentProfile, Enrollment,
    InterestForm, ContactMessage, Webinar, WebinarRegistration,
    InstructorProfile, CohortInstructor, Assignment, AssignmentSubmission
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_weeks', 'price', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


class CohortInstructorInline(admin.TabularInline):
    model = CohortInstructor
    extra = 1


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'start_date', 'end_date', 'status', 'enrollment_count', 'spots_remaining']
    list_filter = ['status', 'start_date', 'course']
    search_fields = ['name', 'course__title']
    readonly_fields = ['created_at', 'enrollment_count', 'spots_remaining']
    inlines = [CohortInstructorInline]
    
    def enrollment_count(self, obj):
        return obj.current_enrollment_count
    enrollment_count.short_description = 'Enrolled'
    
    def spots_remaining(self, obj):
        remaining = obj.spots_remaining
        color = 'green' if remaining > 5 else 'orange' if remaining > 0 else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            remaining
        )
    spots_remaining.short_description = 'Spots Left'


@admin.register(WeekCurriculum)
class WeekCurriculumAdmin(admin.ModelAdmin):
    list_display = ['course', 'week_number', 'title']
    list_filter = ['course']
    search_fields = ['title', 'description']
    ordering = ['course', 'week_number']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'tech_skill_level', 'owns_smartphone', 'owns_computer', 'created_at']
    list_filter = ['tech_skill_level', 'owns_smartphone', 'owns_computer', 'preferred_contact']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'cohort', 'status', 'payment_status', 
        'amount_paid', 'assessment_call_date', 'enrolled_at'
    ]
    list_filter = ['status', 'cohort__course', 'payment_date', 'enrolled_at']
    search_fields = [
        'student__username', 'student__email', 
        'student__first_name', 'student__last_name',
        'cohort__name'
    ]
    readonly_fields = ['enrolled_at', 'updated_at']
    
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('student', 'cohort', 'status')
        }),
        ('Payment Details', {
            'fields': ('amount_paid', 'payment_method', 'payment_date')
        }),
        ('Assessment', {
            'fields': ('assessment_call_date', 'assessment_notes')
        }),
        ('Progress', {
            'fields': ('attendance_count', 'assignments_completed')
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_status(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: green;">✓ Paid</span>')
        else:
            return format_html('<span style="color: red;">✗ Pending</span>')
    payment_status.short_description = 'Payment'
    
    actions = ['mark_as_enrolled', 'mark_as_paid']
    
    def mark_as_enrolled(self, request, queryset):
        queryset.update(status='enrolled')
        self.message_user(request, f'{queryset.count()} enrollment(s) marked as enrolled.')
    mark_as_enrolled.short_description = 'Mark selected as enrolled'
    
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        for enrollment in queryset:
            if enrollment.amount_paid == 0:
                enrollment.amount_paid = enrollment.cohort.course.price
                enrollment.payment_date = timezone.now()
                enrollment.save()
        self.message_user(request, f'{queryset.count()} enrollment(s) marked as paid.')
    mark_as_paid.short_description = 'Mark selected as paid'


@admin.register(InterestForm)
class InterestFormAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'phone_number', 'interested_course',
        'contacted', 'converted_to_enrollment', 'created_at'
    ]
    list_filter = ['contacted', 'converted_to_enrollment', 'how_did_you_hear', 'interested_course', 'created_at']
    search_fields = ['full_name', 'email', 'phone_number']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone_number', 'age')
        }),
        ('Interest Details', {
            'fields': ('interested_course', 'preferred_cohort', 'how_did_you_hear', 'message')
        }),
        ('Status', {
            'fields': ('contacted', 'converted_to_enrollment')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_contacted', 'mark_as_converted']
    
    def mark_as_contacted(self, request, queryset):
        queryset.update(contacted=True)
        self.message_user(request, f'{queryset.count()} lead(s) marked as contacted.')
    mark_as_contacted.short_description = 'Mark as contacted'
    
    def mark_as_converted(self, request, queryset):
        queryset.update(converted_to_enrollment=True)
        self.message_user(request, f'{queryset.count()} lead(s) marked as converted.')
    mark_as_converted.short_description = 'Mark as converted to enrollment'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_responded', 'created_at']
    list_filter = ['is_responded', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'responded_at']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'phone', 'subject', 'message')
        }),
        ('Response', {
            'fields': ('is_responded', 'response', 'responded_at')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_responded']
    
    def mark_as_responded(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_responded=True, responded_at=timezone.now())
        self.message_user(request, f'{queryset.count()} message(s) marked as responded.')
    mark_as_responded.short_description = 'Mark as responded'


class WebinarRegistrationInline(admin.TabularInline):
    model = WebinarRegistration
    extra = 0
    readonly_fields = ['full_name', 'email', 'phone', 'registered_at']
    can_delete = False


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'registration_count', 'spots_remaining', 'is_active']
    list_filter = ['is_active', 'date']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'registration_count', 'spots_remaining']
    inlines = [WebinarRegistrationInline]
    
    def registration_count(self, obj):
        return obj.registration_count
    registration_count.short_description = 'Registrations'
    
    def spots_remaining(self, obj):
        remaining = obj.spots_remaining
        color = 'green' if remaining > 10 else 'orange' if remaining > 0 else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            remaining
        )
    spots_remaining.short_description = 'Spots Left'


@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'webinar', 'attended', 'enrolled_after', 'registered_at']
    list_filter = ['attended', 'enrolled_after', 'webinar', 'registered_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['registered_at']
    
    actions = ['mark_as_attended']
    
    def mark_as_attended(self, request, queryset):
        queryset.update(attended=True)
        self.message_user(request, f'{queryset.count()} registration(s) marked as attended.')
    mark_as_attended.short_description = 'Mark as attended'


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'university', 'monthly_rate', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'university']
    readonly_fields = ['joined_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'cohort', 'week_number', 'due_date']
    list_filter = ['cohort', 'week_number']
    search_fields = ['title', 'description']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'completed', 'score', 'submitted_at']
    list_filter = ['completed', 'assignment__cohort', 'assignment__week_number']
    search_fields = ['student__username', 'student__email', 'assignment__title']
    readonly_fields = ['submitted_at', 'graded_at']