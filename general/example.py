from django_q.tasks import async_task

async_task('time.sleep', 22)
