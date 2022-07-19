from django import forms


class JsonForm(forms.Form):
    api_client_class = None

    field_class_map = {
        "text": (forms.CharField, None),
        "checkbox": (forms.BooleanField, None),
        None: (forms.CharField, forms.Textarea),
        "select": (forms.ChoiceField),
    }
    
    def __init__(self, initial=None, *args, **kwargs):
        self.api_client = self.get_api_client()
        self.api_form = self.get_api_form(self.api_client)
        self.api_fields = self.get_api_fields(self.api_form)
        self.api_initial = self.get_api_initial(self.api_form)
        self.api_success_data=None

        initial = initial or self.api_initial

        super().__init__(initial=initial, *args, **kwargs)

        self.create_fields(self.api_fields)

    def get_api_client(self):
        api_client_class = self.get_api_client_class()

        return api_client_class(**self.get_api_client_kwargs())

    def get_api_client_kwargs(self):
        return {}

    def get_api_client_class(self):
        assert self.api_client_class is not None, (
            f"{self.__class__} must define .api_client_class"
        )
        return self.api_client_class

    def get_api_form(self, api_client):
        data = api_client.get(**self.get_api_form_kwargs())
        return data["form"]

    def get_api_form_kwargs(self):
        return {}

    def get_api_fields(self, api_form):
        return api_form["fields"]

    def get_api_initial(self, api_form):
        return api_form["data"]

    def create_fields(self, api_fields):
        for api_field in api_fields:
            input_type = api_field.pop("input_type")
            input_name = api_field.pop("name")

            # We depend on the API to tell us if a field is required
            api_field["required"] = False

            field_class = self.get_field_class(input_type)
            field_kwargs = {}

            if isinstance(field_class, (tuple, list)):
                field_class, widget = field_class
                field_kwargs["widget"] = widget

            field_kwargs.update(api_field)

            field = field_class(**field_kwargs)

            self.fields[input_name] = field

    def get_field_class(self, input_type):
        return self.field_class_map[input_type]

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)

        # Send the data to the API
        try:
            self.api_success_data = self.api_client.post(**self.cleaned_data)
        except self.api_client.ApiClientException as e:
            errors = e.response_data["form"]["errors"]
            
            for field_name, errors in errors.items():
                if field_name == "__all__":
                    field_name = None

                for error in errors:
                    self.add_error(field_name, error)
