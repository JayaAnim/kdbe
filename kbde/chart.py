from kbde.data import mixins as data_mixins
from kbde import json as kbde_json

import json


try:
    import django
except ImportError:
    django = None


class Point(data_mixins.Serialize):
    serialize_fields = [
        "x", "y",
        ]

    def __init__(self, x, y):
        self.x = x
        self.y = y


class BoundDataset(data_mixins.Serialize):

    def __init__(self, chart, dataset):
        self.chart = chart
        self.dataset = dataset

        # Make sure that the dataset subscribes to a point_set if there are many
        if len(self.chart.point_map.keys()) > 1:
            assert self.dataset.point_set is not None, f"dataset `{self.dataset.__class__.__name__}` must define `point_set` when there are multiple in `chart.point_map`"

            self.points = self.chart.point_map[self.dataset.point_set]

        else:
            self.points = self.chart.point_map[next(iter(self.chart.point_map))]

    def serialize(self):
        return self.dataset.serialize(self.points)


class Dataset(data_mixins.Serialize):
    dataset_type = None

    def __init__(self, point_set=None, label=None, color=None):
        self.point_set = point_set
        self.label = label
        self.color = color

    def serialize(self, points):
        return {
            "dataset_type": self.dataset_type,
            "label": self.label,
            "color": self.color,
            }

    def get_points(self, points):
        return points

    def get_point_class(self):
        return self.point_class


class Chart(data_mixins.Serialize):
    point_class = Point
    options = {}

    def __init__(self, point_map):
        assert isinstance(point_map, dict), "`point_map` must be a dict"

        self.point_map = point_map
        self.datasets = self.get_datasets()
        self.bound_datasets = self.get_bound_datasets()

    def to_json(self):
        return json.dumps(self, cls=kbde_json.Encoder)

    def serialize(self):
        return {
            "options", self.options,
            "datasets", self.bound_datasets,
            }

    def get_bound_datasets(self):
        bound_datasets = []

        for dataset in self.datasets:
            bound_dataset = BoundDataset(self, dataset)
            bound_datasets.append(bound_dataset)

        return bound_datasets

    def get_datasets(self):
        datasets = []

        for key in dir(type(self)):
            dataset = getattr(self, key)

            if not isinstance(dataset, Dataset):
                continue

            datasets.append(dataset)

        assert datasets, f"{self.__class__.__name__} does not define any datasets"

        return datasets

    def get_point_class(self):
        return self.point_class


class PairChart(Chart):

    def __init__(self, pair_map):
        point_map = {}
        point_class = self.get_point_class()

        for set_name, pair_set in pair_map.items():
            point_map[set_name] = [point_class(*pair) for pair in pair_set]

        return super().__init__(point_map)


class QuerysetChart(PairChart):
    
    def __init__(self, queryset_map):
        pair_map = {}
        
        for set_name, queryset in queryset_map.items():
            pairs = []
            for i, pair in enumerate(queryset):
                pair_len = len(pair)

                assert pair_len > 0, "pairs cannot be empty"
                assert pair_len < 3, "pairs cannot have more than 2 items"

                if pair_len == 1:
                    pair = (i+1, pair[0])

                pairs.append(pair)

            pair_map[set_name] = pairs

        return super().__init__(pair_map)


class ModelChart(Chart):
    pass
