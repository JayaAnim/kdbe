from django import utils, urls
from django.db import models
from django.core import files
from polymorphic import models as poly_models
from kbde.django import models as kbde_models

from . import renderers

import tempfile, uuid, os, datetime


def get_report_upload_to(obj, file_name):
    return f"report/{uuid.uuid4()}/{file_name}"


class Report(poly_models.PolymorphicModel):
    # The human-readable name of the report
    title = None

    # Description of this report
    description = None

    # The base model for the report
    model = None

    # The fields that each resultant object will have
    output_fields = []

    # Default number of records per database query
    page_size_default = 100000

    # Number of seconds between progress updates
    progress_update_interval = 5

    # Update URL name
    update_url_name = None

    # Model fields
    slug = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD)
    record_count = models.IntegerField(null=True, blank=True)
    renderer = models.CharField(max_length=kbde_models.MAX_LENGTH_CHAR_FIELD,
                                choices=renderers.CHOICES)
    records_complete = models.IntegerField(default=0)
    result = models.FileField(upload_to=get_report_upload_to, null=True, blank=True)

    time_started = models.DateTimeField(null=True, blank=True)
    time_completed = models.DateTimeField(null=True, blank=True)

    # Status fields
    STATUS_NEW = 0
    STATUS_PENDING = 1
    STATUS_RUNNING = 2
    STATUS_FINISHED = 3
    STATUS_FAILED = 4
    STATUS_CHOICES = (
        (STATUS_NEW, "Created"),
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_FINISHED, "Finished"),
        (STATUS_FAILED, "Failed"),
        )
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_NEW)

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        assert self.title, f"Report, {self.__class__.__name__}, must define self.title"
        assert self.model, f"Report, {self.__class__.__name__}, must define self.model"
        assert issubclass(self.model, models.Model), ("self.model in {self.__class__.__name__} "
                                                      "must be a Django model")

        super().save(*args, **kwargs)

    def schedule_process(self):
        self.status = self.STATUS_PENDING
        self.save()

        is_async = not settings.RQ_SYNC
        q = django_rq.get_queue("report", is_async=is_async)
        return q.enqueue(process_report, self.id)

    def process(self):
        self.status = self.STATUS_RUNNING
        self.time_started = utils.timezone.now()
        self.save()

        try:
            # Set row count
            self.set_row_count()
            # Get data
            data = self.get_data()
            # Render
            result_file_path, file_extension = self.write_result_file(data)
            # Save
            self.save_result_file(result_file_path, file_extension)

        except Exception:
            self.status = self.STATUS_FAILED
            self.save()
            raise

        # Cleanup
        os.remove(result_file_path)

        self.status = self.STATUS_FINISHED
        self.time_completed = utils.timezone.now()
        self.save()

    def set_row_count(self):
        self.record_count = self.get_record_count()
        self.save()

    def get_data(self, page=None):
        if page is None:
            data = self.get_all_pages()
        else:
            data = self.get_page(page)

        output_fields = self.get_output_fields()

        for row in data:
            yield {field_name: getattr(row, field_name) for field_name in output_fields}

    def get_all_pages(self):
        page = 1
        page_size = self.get_page_size_default()

        while True:
            page_result = self.get_page(page, page_size)

            if not page_result:
                break

            for row in page_result:
                yield row

            page += 1

    def get_page(self, page_number, page_size):
        """
        Returns a single page of a report
        Takes the page number as well as the page_size (number of records per page)
        returns a list of model objects
        """
        start_index = self.get_start_index(page_number, page_size)
        end_index = self.get_end_index(page_number, page_size)

        queryset = self.get_queryset()

        """
        if sorts:
            queryset = queryset.order_by(*sorts)
        """

        return queryset[start_index:end_index]

    def write_result_file(self, data):
        update_interval = datetime.timedelta(seconds=self.progress_update_interval)
        next_update = datetime.datetime.now() + update_interval

        with tempfile.NamedTemporaryFile("w", delete=False, prefix="report_") as temp:
            renderer_cls = self.get_renderer()
            renderer = renderer_cls(temp, self.get_output_fields())
            
            for i, row in enumerate(data):

                if datetime.datetime.now() >= next_update:
                    self.records_complete = i
                    self.save()
                    next_update += update_interval

                renderer.write_row(row)

        self.records_complete = i + 1
        self.save()

        return temp.name, renderer.file_extension

    def save_result_file(self, result_file_path, file_extension):
        with open(result_file_path, "rb") as temp:
            # Get the django file
            django_file = files.File(temp)
            # Get the result file name (extension comes from the renderer name)
            result_file_name = f"{self.title}.{file_extension}"
            # Save the file
            self.result.save(result_file_name, django_file, save=True)

    def get_progress_percentage(self):
        if not self.record_count or not self.records_complete:
            return 0.0
        return self.records_complete / self.record_count

    def get_output_fields(self):
        return self.output_fields.copy()
            
    def get_renderer(self):
        return renderers.MAP[self.renderer]

    def get_record_count(self):
        return self.get_queryset().count()

    def get_queryset(self):
        """
        Filters the queryset based on the values on this model
        Returns the queryset
        """
        return self.model.objects.all()

    def get_update_url(self):
        if self.update_url_name:
            return urls.reverse(self.update_url_name, args=[self.slug])

    # Base helpers

    def get_page_size_default(self):
        return self.page_size_default

    def get_end_index(self, page, page_size):
        """
        Takes page and page size and calculates the limit
        """
        start_index = self.get_start_index(page, page_size)
        return start_index + page_size

    def get_start_index(self, page, page_size):
        """
        Takes page and page size and calculates the offset
        """
        return (page - 1) * page_size
