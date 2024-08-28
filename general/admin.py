from django.contrib import admin
from .models import JobExecution, ScheduledJob, Email, Target, Project, Subproject, Task, TaskChunk

# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Project, ProjectAdmin)


class SubprojectAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Subproject, SubprojectAdmin)

class EmailAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.register(Email, EmailAdmin)


class TargetAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.register(Target, TargetAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'my_email',)


admin.site.register(Task, TaskAdmin)


class TaskChunkAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(TaskChunk, TaskChunkAdmin)


admin.site.register(ScheduledJob)

admin.site.register(JobExecution)