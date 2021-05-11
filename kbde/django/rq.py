from django.conf import settings


def queue_task(queue_name, task_func, **kwargs):
    """
    Queues a task to run the given function, passing **kwargs as the arguments
    """
    import django_rq

    is_async = not settings.RQ_SYNC
    queue = django_rq.get_queue(queue_name, is_async=is_async)

    return queue.enqueue(task_func, **kwargs)


def schedule_task_in(queue_name, task_func, queue_in, **kwargs):
    """
    Schedules a task to run the given function in a given amount of time, passing **kwargs as the arguments
    """
    import django_rq, rq_scheduler

    is_async = not settings.RQ_SYNC
    assert is_async, "cannot use the task scheduler synchronously"

    scheduler = django_rq.get_scheduler(queue_name)

    return scheduler.enqueue_in(queue_in, task_func, **kwargs)


def schedule_task_at(queue_name, task_func, queue_at, **kwargs):
    """
    Schedules a task to run the given function a given time, passing **kwargs as the arguments
    """
    import django_rq, rq_scheduler

    is_async = not settings.RQ_SYNC
    assert is_async, "cannot use the task scheduler synchronously"

    scheduler = django_rq.get_scheduler(queue_name)

    return scheduler.enqueue_at(queue_at, task_func, **kwargs)
