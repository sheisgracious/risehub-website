# info_site/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('interest/', views.interest_form_view, name='interest_form'),
    path('contact/', views.contact_view, name='contact'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    
    # Webinar pages
    path('webinars/', views.webinar_list_view, name='webinar_list'),
    path('webinar/<int:webinar_id>/register/', views.webinar_registration_view, name='webinar_register'),
    
    # Authentication
    path('register/', views.student_registration_view, name='student_register'),
    path('login/', auth_views.LoginView.as_view(template_name='info_site/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Student portal
    path('dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('profile/', views.student_profile_view, name='student_profile'),
    path('enroll/', views.enrollment_view, name='enrollment'),
    path('enrollment/<int:enrollment_id>/payment/', views.enrollment_payment_view, name='enrollment_payment'),
    path('cohort/<int:cohort_id>/materials/', views.cohort_materials_view, name='cohort_materials'),
]