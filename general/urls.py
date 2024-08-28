from django.urls import path, include, re_path
from .views import *
from users.views import *

app_name = 'general'

urlpatterns = [
    path('', dashboard, name='home'),
    path('login/', user_login, name='login'),
    path('login_otp/', login_otp, name='login-otp'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('add/project', add_project, name='add_project'),
    path('add/subproject', add_subproject, name='add_subproject'),
    path('in/', side_in, name='in'),
    path('in/add-email', add_email, name='add-email'),
    path('in/delete-email/<int:email_id>/', delete_email, name='delete-email'),
    path('out/', side_out, name='out'),
    path('out/add-email-target', add_email_target, name='add-email-target'),
    path('out/add-email-target-csv', add_email_target_csv, name='add-email-target-csv'),
    path('out/download-target-csv', download_sample_target_csv, name='download-target-csv'),
    path('out/upload-target-csv', simple_upload, name='upload-target-csv'),
    path('out/delete-email-target/<int:target_id>/', delete_email_target, name='delete-email-target'),
    path('schedule/', schedule_list, name='schedule'),
    path('schedule/ajax/<int:id>/', schedule_get_target, name='get_target'),
    path('add-task/', add_task, name='add-task'),
    path('add-task/auto/', add_auto_task, name='add-auto-task'),
    path('add-schedule/', add_schedule_task, name='add-schedule'),
    path('delete-task/<int:task_id>/', delete_task, name='delete-task'),
    path('delete-schedule/<str:job_id>/', delete_schedule_task, name='delete-schedule'),
]
