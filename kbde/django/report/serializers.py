from rest_framework import serializers


class Report(serializers.ModelSerializer):
    
    status_display = serializers.CharField(source="get_status_display")
    progress_percentage = serializers.DecimalField(source="get_progress_percentage",
                                                   max_digits=10,
                                                   decimal_places=7)
    
    class Meta:
        fields = [
            "id",
            "slug",
            "name",
            "title",
            "status",
            "status_display",
            "time_started",
            "record_count",
            "records_complete",
            "progress_percentage",
            "time_completed",
            "result",
            ]
