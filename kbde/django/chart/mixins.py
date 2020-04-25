

class Chart:
    chart_class = None
    
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data["chart_id"] = self.get_chart_id(context_data)
        context_data["chart"] = self.get_chart(context_data)

        return context_data

    def get_chart_id(self, context_data):
        return 0

    def get_chart(self, context_data):
        return self.get_chart_class()(self.get_chart_map(context_data))

    def get_chart_class(self):
        return self.chart_class

    def get_chart_map(self, context_data):
        raise NotImplementedError(f"{self.__class__.__name__} must implement `get_chart_map()`")


class Queryset(Chart):
    
    def get_chart_map(self, context_data):
        return {"queryset": context_data["object_list"]}
