from kbde import chart


class Dataset(chart.Dataset):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assert self.label is not None, "must provide `label` for dataset"
        assert self.dataset_type is not None, "must provide `dataset_type` for dataset"
    
    def serialize(self, points):
        data = {
            "label": self.label,
            "type": self.dataset_type,
            "data": [point.y for point in points],
            "backgroundColor": self.color,
            "borderColor": self.color,
            "fill": False,
            }

        return data


class Bar(Dataset):
    dataset_type = "bar"

class Line(Dataset):
    dataset_type = "line"


class SteppedLineDataset(Dataset):
    
    def __init__(self, stepped_line, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stepped_line = stepped_line
    
    def serialize(self):
        data = super().serialize()
        data["steppedLine"] = self.stepped_line
        return data


class ChartBase:
    dataset_class = Dataset

    def serialize(self):
        data = {
            "type": self.datasets[0].dataset_type,
            "data": {
                "datasets": self.bound_datasets,
                },
            "options": self.options,
            }
        
        data["data"]["labels"] = [point.x for point in self.bound_datasets[0].points]

        return data


class Chart(ChartBase, chart.Chart):
    """
    Basic Chart
    """


class QuerysetChart(ChartBase, chart.QuerysetChart):
    """
    Queryset
    """
