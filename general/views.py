from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Email, Target, Project, Subproject, Task, TaskChunk, ScheduledJob, JobExecution
from users.models import User
import django_q.models
import os
import mimetypes
from django.http import HttpResponse
import csv
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import smtplib
from split import chop
from unique_names_generator import get_random_name
from datetime import datetime, timedelta
from django.http import JsonResponse
from django_q.models import Schedule
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from .emails import send_email
from apscheduler.events import EVENT_JOB_EXECUTED
from .tasks import send_target_emails, check_my_email


@login_required(login_url='general:login')
def dashboard(request):
    if request.user.is_authenticated:
        projects = Project.objects.all()
        emails_count = Email.objects.all().count()
        projects_count = Project.objects.all().count()
        targets_count = Target.objects.all().count()
        users_count = User.objects.count()

        context = {'projects': projects,
                   'emails_count': emails_count,
                   'projects_count': projects_count,
                   'targets_count': targets_count,
                   'users_count': users_count,
                   }
        return render(request, 'dashboard.html', context)


@login_required(login_url='general:login')
def profile(request):
    if request.user.is_superuser:
        users = User.objects.all()
        sub_projects = Subproject.objects.all()
        user = get_object_or_404(User, email=request.user)
    else:
        user = get_object_or_404(User, email=request.user)
        sub_projects = Subproject.objects.filter(user=request.user)
        users = None

    context = {'users': users, 'user': user, 'sub_projects': sub_projects}
    return render(request, 'auth/profile.html', context)


@login_required(login_url='general:login')
def side_in(request):
    if request.user.is_superuser:
        sub_projects = Subproject.objects.all()
        emails = Email.objects.all()
    else:
        sub_projects = Subproject.objects.filter(user=request.user)
        emails = Email.objects.filter(project__user=request.user)

    projects = Project.objects.all()
    context = {'emails': emails, 'projects': projects, 'sub_projects': sub_projects}
    return render(request, 'in.html', context)


@login_required(login_url='general:login')
def add_project(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == 'POST':
                # try:
                project_name = request.POST.get('project_name')

                Project.objects.create(name=project_name, user=request.user)

                messages.success(request, "project added successfully")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def add_subproject(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # try:
            subproject_name = request.POST.get('project_name')
            subproject_project = request.POST.get('subproject_project')
            pro = get_object_or_404(Project, name=subproject_project)
            Subproject.objects.create(name=subproject_name, project=pro, user=request.user)

            messages.success(request, "project added successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def add_email(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # try:
            email_project = request.POST.get('email-project')
            email_title = request.POST.get('email-title')
            email_value = request.POST.get('email_value')
            password_value = request.POST.get('password_value')
            host_value = request.POST.get('host_value')
            port_value = request.POST.get('port_value')

            pro = get_object_or_404(Subproject, name=email_project, user=request.user)
            Email.objects.create(project=pro, title=email_title, host_server=host_value, port_server=port_value, email=email_value, password=password_value)

            messages.success(request, "email added successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def delete_email(request, email_id):
    if request.user.is_authenticated:
        # Retrieve the email object you want to delete
        email_object = get_object_or_404(Email, pk=email_id)

        # Check if the user owns this email (optional, depending on your logic)
        if email_object.project.user == request.user:
            # Delete the email object
            email_object.delete()

            messages.success(request, "Email deleted successfully")
        else:
            messages.error(request, "You don't have permission to delete this email")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def side_out(request):
    targets = Target.objects.all().order_by('project')
    if request.user.is_superuser:
        sub_projects = Subproject.objects.all()
    else:
        sub_projects = Subproject.objects.filter(user=request.user)
    projects = Project.objects.all()
    context = {'targets': targets, 'projects':projects, 'sub_projects':sub_projects}
    return render(request, 'out.html', context)


@login_required(login_url='general:login')
def add_email_target(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # try:
            target_project = request.POST.get('target-project')
            target_title = request.POST.get('target-title')
            target_email = request.POST.get('target-email')
            target_name = request.POST.get('target-name')
            target_lastname = request.POST.get('target-lastname')
            target_phone = request.POST.get('target-phone')
            target_other = request.POST.get('target-other')

            pro = get_object_or_404(Subproject, name=target_project)
            if not Target.objects.filter(project=pro, email=target_email).exists():
                Target.objects.create(project=pro, title=target_title, email=target_email, name=target_name, lastname=target_lastname, phone=target_phone, other=target_other)

            messages.success(request, "email added successfully")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def add_email_target_csv(request):
    sub = request.POST.get('target-subproject')
    pro = get_object_or_404(Subproject, name=sub)
    # Code to load the data into database
    with open('./media/target.csv', mode='r') as file:
        csvFile = csv.reader(file)
        next(csvFile, None)  # skip the headers
        for lines in csvFile:
            if not Target.objects.filter(project=pro, email=lines[1]).exists():
                target = Target(project=pro, title=lines[0], email=lines[1], name=lines[2], lastname=lines[3], phone=lines[4], other=lines[5])
                target.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def simple_upload(request):
    if request.method == 'POST':
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def download_sample_target_csv(request):
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    filename = 'target.csv'
    # Define the full file path
    filepath = BASE_DIR + '/download_app/Files/' + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response


@login_required(login_url='general:login')
def schedule_list(request):
    # schedule = django_q.models.Schedule.objects.all()
    schedule = ScheduledJob.objects.all()
    # successful = django_q.models.Task.objects.all()
    successful = JobExecution.objects.all()
    projects = Subproject.objects.all()
    task = Task.objects.all()
    emails = Email.objects.all()
    targets = Target.objects.all()
    context = {'successful': successful, 'schedule': schedule, 'emails': emails, 'targets': targets, 'task': task, 'projects': projects}
    return render(request, 'scheduler.html', context)


@login_required(login_url='general:login')
def schedule_get_target(request, id):
    if id == 0:
        targets = Target.objects.all()
    else:
        pro = get_object_or_404(Subproject, pk=id)
        targets = Target.objects.filter(project=pro)

    data = list(targets.values('id', 'name'))  # Convert queryset to a list of dictionaries

    return JsonResponse({'targets': data})


@login_required(login_url='general:login')
def delete_email_target(request, target_id):
    if request.user.is_authenticated:
        # Retrieve the target object you want to delete
        target_object = get_object_or_404(Target, pk=target_id)

        # Check if the user owns this target (optional, depending on your logic)
        if target_object.project.user == request.user:
            # Delete the target object
            target_object.delete()

            messages.success(request, "Target deleted successfully")
        else:
            messages.error(request, "You don't have permission to delete this target")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def add_schedule_task(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            def on_job_execution(event):
                if event.code == EVENT_JOB_EXECUTED:
                    job_result = event.retval
                    execution_time = datetime.now()
                    job_id = str(event.job_id)  # Convert job ID to string

                    # Save job execution details in the database
                    job_execution = JobExecution(job_id=job_id, execution_time=execution_time, job_result=job_result)
                    job_execution.save()

            schTask = request.POST.getlist('schedule_task')
            schStart = request.POST.get('schedule_start')
            schStart = timezone.make_aware(datetime.strptime(schStart, '%Y-%m-%dT%H:%M'))

            schDelay = request.POST.get('schedule_delay')
            schCheck = request.POST.get('schedule_check')

            for email in schTask:

                t = get_object_or_404(Task, name=email)

                check_count = 0
                time_mem = []
                time_mem.append(schStart)
                for tsk in t.target_list.all():
                    scheduler = BackgroundScheduler()
                    ch = TaskChunk.objects.create(name=get_random_name(), email=t.my_email, target=tsk, task=t)
                    job = scheduler.add_job(send_target_emails, 'date', run_date=time_mem[0], args=[ch.id])

                    # Attach event listener to capture job execution details
                    scheduler.add_listener(on_job_execution, mask=EVENT_JOB_EXECUTED)

                    # Save job details in the model
                    scheduled_job = ScheduledJob(job_task_chunk=ch, job_id=job.id, next_run_time=time_mem[0])
                    scheduled_job.save()

                    scheduler.start()
                    # Add x minutes
                    current_time = time_mem[0] + timedelta(minutes=int(schDelay))
                    time_mem.remove(time_mem[0])
                    time_mem.append(current_time)


                    if not int(schCheck) <= 0:
                        if int(schCheck) == check_count:
                            scheduler = BackgroundScheduler()
                            ch = TaskChunk.objects.create(name='CHECK', email=t.my_email, task=t)
                            job = scheduler.add_job(check_my_email, 'date', run_date=time_mem[0], args=[ch.id])

                            # Attach event listener to capture job execution details
                            scheduler.add_listener(on_job_execution, mask=EVENT_JOB_EXECUTED)

                            # Save job details in the model
                            scheduled_job = ScheduledJob(job_task_chunk=ch, job_id=job.id, next_run_time=time_mem[0])
                            scheduled_job.save()

                            scheduler.start()
                            check_count = 0

                        check_count += 1

                t.delay = schDelay
                t.check_mail = schCheck
                t.save()  # Save the changes to the database


    return redirect("general:schedule")


@login_required(login_url='general:login')
def delete_schedule_task(request, job_id):
    if request.user.is_authenticated:
        scheduler = BackgroundScheduler()
        try:
            scheduler.remove_job(job_id)

            scheduled_job = ScheduledJob.objects.get(job_id=job_id)
            scheduled_job.delete()

            messages.success(request, "Scheduler deleted successfully")
        except Exception as e:
            # scheduler.shutdown()
            print(f"Error deleting job {job_id}: {e}")
            messages.error(request, "You don't have permission to delete this Scheduler")
        finally:
            scheduled_job = ScheduledJob.objects.get(job_id=job_id)
            scheduled_job.delete()
            messages.error(request, "You don't have permission to delete this Scheduler")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='general:login')
def add_task(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            tskEmail = request.POST.getlist('task_emails')
            tskTargets = request.POST.getlist('task_targets')
            tskMsg = request.POST.get('task_message')
            uploaded_file = request.FILES['add_task_file']

            #
            num_emails = len(tskEmail)
            num_targets = len(tskTargets)

            # Calculate the number of targets per email
            targets_per_email = num_targets // num_emails
            remaining_targets = num_targets % num_emails

            target_index = 0
            task_name = ''
            list_emials = []
            numbers = list(chop(targets_per_email, tskTargets))

            # Assign targets to emails
            for email in tskEmail:
                myMail = Email.objects.get(email=email)
                _task = Task.objects.create(name=get_random_name(), my_email=myMail, message=tskMsg, template=uploaded_file , user=request.user)
                task_name = str(_task.id)
                for j in numbers:
                    list_emials.append(j)
                    for k in j:
                        t = Target.objects.get(pk=int(k))
                        _task.target_list.add(t)
                    numbers.remove(j)
                    break


            __task = get_object_or_404(Task, pk=int(task_name))
            for j in numbers:
                for k in j:
                    t = Target.objects.get(pk=int(k))
                    __task.target_list.add(t)
                numbers.remove(j)
                break
    return redirect("general:schedule")


@login_required(login_url='general:login')
def add_auto_task(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            target_pro = request.POST.get('target-pro')
            uploaded_file = request.FILES['add_auto_task_file']

            list_my_emials = Email.objects.filter(project__name=target_pro)
            target_list = Target.objects.filter(project__name=target_pro)

            list_emials = []
            numbers = list(chop(4, target_list))

            for i in list_my_emials:
                username = i.email
                myMail = Email.objects.get(email=username)
                _task = Task.objects.create(name=get_random_name(), my_email=myMail, user=request.user, template=uploaded_file)
                for j in numbers:
                    list_emials.append(j)
                    for k in j:
                        target = Target.objects.get(email=k)
                        _task.target_list.add(target.id)
                    numbers.remove(j)
                    break

            # r = int((target_list.count() / 4) + 1)

    return redirect("general:schedule")


@login_required(login_url='general:login')
def delete_task(request, task_id):
    if request.user.is_authenticated:
        # Retrieve the task object you want to delete
        task_object = get_object_or_404(Task, pk=task_id)

        # Check if the user owns this task (optional, depending on your logic)
        if task_object.user == request.user:
            # Delete the task object
            task_object.delete()

            messages.success(request, "Task deleted successfully")
        else:
            messages.error(request, "You don't have permission to delete this task")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

