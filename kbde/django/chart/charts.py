from django.db.models import F


class Chart:
    
    def __init__(self, queryset):
        self.queryset = queryset

    def serialize(self):
        return {
            "data": {
                "datasets": self.get_bound_datasets(),
            },
        }

    def get_bound_datasets(self):
        datasets = self.get_datasets()
        return [
            BoundDataset(self, dataset, field_name)
            for field_name, dataset in datasets.items()
        ]
    
    def get_datasets(self):
        datasets = {}

        for attr, value in self.__class__.__dict__.items():

            if not isinstance(value, Dataset):
                continue

            datasets[attr] = value

        return datasets

    def get_queryset(self):
        return self.queryset


class Dataset:
    chart_type = None

    def __init__(self,
                 x_key,
                 y_key,
                 label=None,
                 background_color=None,
                 border_color=None,
                 color=None):
        self.x_key = x_key
        self.y_key = y_key
        self.label = label
        self.background_color = background_color
        self.border_color = border_color
        self.color = color

    def serialize(self):
        data = {
            "type": self.get_chart_type(),
        }
        
        config = self.get_config()
        config = {key: value for key, value in config.items() if value is not None}

        data.update(config)

        return data

    def get_config(self):
        return {
            "backgroundColor": self.get_background_color(),
            "borderColor": self.get_border_color(),
            "color": self.get_color(),
        }

    def get_chart_type(self):
        assert self.chart_type is not None, (
            f"{self.__class__} must define .chart_type"
        )
        return self.chart_type
        
    def get_label(self):
        return self.label

    def get_data(self, queryset):
        expressions = {
            "x": F(self.get_x_key()),
            "y": F(self.get_y_key()),
        }
        return queryset.annotate(**expressions).values(*expressions.keys())

    def get_x_key(self):
        return self.x_key

    def get_y_key(self):
        return self.y_key

    def get_background_color(self):
        return self.background_color

    def get_border_color(self):
        return self.border_color

    def get_color(self):
        return self.color


class BarDataset(Dataset):
    chart_type = "bar"


class BubbleDataset(Dataset):
    chart_type = "bubble"


class DonutDataset(Dataset):
    chart_type = "donut"


class PieDataset(Dataset):
    chart_type = "pie"


class LineDataset(Dataset):
    chart_type = "line"

    def __init__(self, *args, tension=None, fill=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.tension = tension
        self.fill = fill

    def get_config(self):
        config = super().get_config()

        config.update({
            "tension": self.get_tension(),
            "fill": self.get_fill(),
        })

        return config

    def get_tension(self):
        return self.tension

    def get_fill(self):
        return self.fill


class BoundDataset:
    
    def __init__(self, chart, dataset, field_name):
        self.chart = chart
        self.dataset = dataset
        self.field_name = field_name

    def serialize(self):
        chart = self.get_chart()
        dataset = self.get_dataset()
        return {
            "label": self.get_label(),
            "data": dataset.get_data(chart.get_queryset()),
            **dataset.serialize()
        }

    def get_chart(self):
        return self.chart

    def get_dataset(self):
        return self.dataset

    def get_label(self):
        label = self.dataset.get_label()

        if label is not None:
            return label

        field_name = self.get_field_name()
        field_name = field_name[0].upper() + field_name[1:]
        field_name = field_name.replace("_", " ")

        return field_name

    def get_field_name(self):
        return self.field_name
