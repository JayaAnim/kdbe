from kbde.django import utils as kbde_utils


class Chart:
    x_key = None
    title_text = None
    responsive = True
    maintain_aspect_ratio = False
    
    def __init__(self, queryset):
        self.queryset = queryset

    def serialize(self):
        return {
            "data": self.get_data(),
            "options": self.get_options(),
        }

    def get_data(self):
        return {
            "labels": self.get_labels(),
            "datasets": self.get_bound_datasets(),
        }

    def get_labels(self):
        return [self.get_object_label(obj) for obj in self.get_queryset()]

    def get_object_label(self, obj):
        x_key = self.get_x_key()
        return kbde_utils.get_value_from_object(obj, x_key)

    def get_x_key(self):
        assert self.x_key is not None, (
            f"{self.__class__} must define .x_key"
        )
        return self.x_key

    def get_queryset(self):
        return self.queryset

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

    def get_options(self):
        return {
            "scales": self.get_scales(),
            "plugins": self.get_plugins(),
            "responsive": self.get_responsive(),
            "maintainAspectRatio": self.get_maintain_aspect_ratio(),
        }

    def get_scales(self):
        return {}

    def get_plugins(self):
        return {
            "title": self.get_title(),
        }

    def get_title(self):
        title_text = self.get_title_text()

        return {
            "text": title_text,
            "display": title_text is not None,
        }

    def get_title_text(self):
        return self.title_text

    def get_responsive(self):
        return self.responsive

    def get_maintain_aspect_ratio(self):
        return self.maintain_aspect_ratio


class Dataset:
    chart_type = None

    def __init__(self,
                 y_key,
                 label=None,
                 background_color=None,
                 border_color=None,
                 color=None):
        self.y_key = y_key
        self.label = label
        self.background_color = background_color
        self.border_color = border_color
        self.color = color

    def serialize(self):
        return {
            key: value for key, value in self.get_serialize_data().items()
            if value is not None
        }

    def get_serialize_data(self):
        return {
            "type": self.get_chart_type(),
            "label": self.get_label(),
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

    def get_background_color(self):
        return self.background_color

    def get_border_color(self):
        return self.border_color
    
    def get_color(self):
        return self.color

    def get_data(self, chart):
        return [self.get_object_data(obj) for obj in chart.get_queryset()]

    def get_object_data(self, obj):
        y_key = self.get_y_key()
        return kbde_utils.get_value_from_object(obj, y_key)

    def get_y_key(self):
        return self.y_key


class FillMixin:

    def __init__(self, fill=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fill = fill
        
    def get_serialize_data(self):
        data = super().get_serialize_data()

        data.update({
            "fill": self.get_fill(),
        })

        return data

    def get_fill(self):
        return self.fill


class BarDataset(Dataset):
    chart_type = "bar"


class BubbleDataset(Dataset):
    chart_type = "bubble"
    
    def __init__(self, r_key, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.r_key = r_key
    
    def get_data(self, chart):
        labels = chart.get_labels()
        y_data = super().get_data(chart)
        r_data = self.get_r_data(chart)

        data = []
        for index, label in enumerate(labels):
            data.append({
                "x": label,
                "y": y_data[index],
                "r": r_data[index],
            })

        return data

    def get_r_data(self, chart):
        return [self.get_r_object_data(obj) for obj in chart.get_queryset()]

    def get_r_object_data(self, obj):
        r_key = self.get_r_key()
        return kbde_utils.get_value_from_object(obj, r_key)

    def get_r_key(self):
        return self.r_key


class DoughnutDataset(Dataset):
    chart_type = "doughnut"


class PieDataset(Dataset):
    chart_type = "pie"


class LineDataset(FillMixin, Dataset):
    chart_type = "line"

    def __init__(self, tension=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tension = tension
        
    def get_serialize_data(self):
        data = super().get_serialize_data()

        data.update({
            "tension": self.get_tension(),
        })

        return data

    def get_tension(self):
        return self.tension


class PolarAreaDataset(Dataset):
    chart_type = "polarArea"


class RadarDataset(FillMixin, Dataset):
    chart_type = "radar"


class ScatterDataset(Dataset):
    chart_type = "scatter"
    
    def get_data(self, chart):
        labels = chart.get_labels()
        y_data = super().get_data(chart)

        data = []
        for index, label in enumerate(labels):
            data.append({
                "x": label,
                "y": y_data[index],
            })

        return data


class BoundDataset:
    
    def __init__(self, chart, dataset, field_name):
        self.chart = chart
        self.dataset = dataset
        self.field_name = field_name

    def serialize(self):
        chart = self.get_chart()
        dataset = self.get_dataset()

        bound_dataset = dataset.serialize()

        bound_dataset.update({
            "data": dataset.get_data(chart),
        })

        if bound_dataset.get("label") is None:
            bound_dataset["label"] = self.get_label()

        return bound_dataset

    def get_chart(self):
        return self.chart

    def get_dataset(self):
        return self.dataset

    def get_label(self):
        field_name = self.get_field_name()
        field_name = field_name[0].upper() + field_name[1:]
        field_name = field_name.replace("_", " ")

        return field_name

    def get_field_name(self):
        return self.field_name
