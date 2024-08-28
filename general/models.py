from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

class Project(models.Model):
    """Project Model"""

    name = models.CharField(max_length=20, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def count_subprojects(self):
        return Subproject.objects.filter(project=self).count()

    @property
    def get_target_count(self):
        return Target.objects.filter(project__project=self).count()


class Subproject(models.Model):
    """Sub Project Model"""

    name = models.CharField(max_length=20, blank=False, null=False)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Email(models.Model):
    """Email Model"""

    project = models.ForeignKey("Subproject", on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=20, blank=False, null=False)
    host_server = models.CharField(max_length=100)
    port_server = models.CharField(max_length=5)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['title']


class Target(models.Model):
    """Target Model"""

    project = models.ForeignKey("Subproject", on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=20, blank=False, null=True)
    email = models.EmailField(blank=False, null=True)
    name = models.CharField(max_length=30, blank=False, null=True)
    lastname = models.CharField(max_length=30, blank=False, null=True)
    phone = models.CharField(max_length=20, blank=False, null=True)
    other = models.CharField(max_length=255, blank=False, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['email']


class Task(models.Model):
    """Task for Scheduler"""

    name = models.CharField(max_length=255, blank=False, null=True)
    my_email = models.ForeignKey(Email, on_delete=models.CASCADE, null=True)
    target_list = models.ManyToManyField(Target)
    message = models.TextField()
    template = models.FileField(blank=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    active = models.BooleanField(default=True)
    delay = models.IntegerField(blank=False, null=True)
    check_mail = models.IntegerField(blank=False, null=True)
    run_time = models.DateTimeField(blank=False, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TaskChunk(models.Model):
    """Chunk Task for Scheduler"""

    name = models.CharField(max_length=255, blank=False, null=True)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, null=True)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class ScheduledJob(models.Model):
    job_task_chunk = models.ForeignKey(TaskChunk, on_delete=models.CASCADE, blank=False, null=True)
    job_id = models.CharField(max_length=100)
    next_run_time = models.DateTimeField()

    def __str__(self):
        return f"Job ID: {self.job_id}, Next Run Time: {self.next_run_time}"


class JobExecution(models.Model):
    job_id = models.CharField(max_length=100)
    execution_time = models.DateTimeField()
    job_result = models.TextField()

    def __str__(self):
        return f"Job ID: {self.job_id}, Execution Time: {self.execution_time}"