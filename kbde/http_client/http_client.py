from . import response_handlers

import requests, string


KEY_NOT_FOUND = object()


class HttpClient:
    host = None
    path = None

    headers = {}

    param_keys = []
    data_keys = []
    json_keys = []
    file_keys = []
    
    static_kwargs = {}

    allow_redirects = False

    response_handler_classes = [
        response_handlers.TextResponseHandler,
        response_handlers.JsonResponseHandler,
    ]

    response_status_codes = []

    METHOD_OPTIONS = "OPTIONS"
    METHOD_HEAD = "HEAD"
    METHOD_GET = "GET"
    METHOD_POST = "POST"
    METHOD_PUT = "PUT"
    METHOD_PATCH = "PATCH"
    METHOD_DELETE = "DELETE"

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.session = self.get_session()
        self.latest_response = None

    def get_session(self):
        return requests.Session(**self.get_session_kwargs())

    def get_session_kwargs(self):
        return {}

    def options(self, **kwargs):
        return self.send(self.METHOD_OPTIONS, kwargs)

    def head(self, **kwargs):
        return self.send(self.METHOD_HEAD, kwargs)

    def get(self, **kwargs):
        return self.send(self.METHOD_GET, kwargs)

    def post(self, **kwargs):
        return self.send(self.METHOD_POST, kwargs)

    def put(self, **kwargs):
        return self.send(self.METHOD_PUT, kwargs)

    def patch(self, **kwargs):
        return self.send(self.METHOD_PATCH, kwargs)

    def delete(self, **kwargs):
        return self.send(self.METHOD_DELETE, kwargs)

    def send(self, method, kwargs):
        kwargs = self.get_kwargs(kwargs)

        formatted_url = self.get_formatted_url(kwargs)
        request_kwargs = self.get_request_kwargs(kwargs)

        response = self.get_response(method, formatted_url, request_kwargs)

        self.latest_response = response
        
        response_data = self.get_response_data(response)

        self.check_response(response, response_data)

        return response_data

    def get_kwargs(self, kwargs):
        all_kwargs = {}

        all_kwargs.update(self.static_kwargs)
        all_kwargs.update(self.kwargs)
        all_kwargs.update(kwargs)

        return all_kwargs

    def get_url(self):
        host = self.get_host()
        path = self.get_path()

        return f"{host}{path}"

    def get_host(self):
        return self.host

    def get_path(self):
        return self.path

    def get_formatted_url(self, kwargs):
        url = self.get_url()
        return self.get_formatted_string(url, kwargs)

    def get_request_kwargs(self, kwargs):
        return {
            "allow_redirects": self.get_allow_redirects(),
            "headers": self.get_formatted_headers(kwargs),
            "params": self.get_params(kwargs),
            "data": self.get_data(kwargs),
            "json": self.get_json(kwargs),
            "files": self.get_files(kwargs),
        }

    def get_allow_redirects(self):
        return self.allow_redirects

    def get_formatted_headers(self, kwargs):
        headers = self.get_headers(kwargs)

        for key, value in headers.items():
            headers[key] = self.get_formatted_string(value, kwargs)

        return headers

    def get_headers(self, kwargs):
        return self.headers.copy()
        
    def get_header_keys(self):
        return self.header_keys.copy()

    def get_params(self, kwargs):
        keys = self.get_param_keys()
        return self.get_values_from_kwargs(keys, kwargs)

    def get_param_keys(self):
        return self.param_keys.copy()

    def get_data(self, kwargs):
        keys = self.get_data_keys()
        return self.get_values_from_kwargs(keys, kwargs)

    def get_data_keys(self):
        return self.data_keys.copy()

    def get_json(self, kwargs):
        keys = self.get_json_keys()
        return self.get_values_from_kwargs(keys, kwargs)

    def get_json_keys(self):
        return self.json_keys.copy()

    def get_files(self, kwargs):
        keys = self.get_file_keys()
        return self.get_values_from_kwargs(keys, kwargs)

    def get_file_keys(self):
        return self.file_keys.copy()

    def get_values_from_kwargs(self, keys, kwargs):
        return {key: value for key, value in kwargs.items() if key in keys}

    def get_formatted_string(self, format_string, kwargs):
        string_format_params = self.get_string_format_params(format_string)
        string_format_kwargs = self.get_string_format_kwargs(
            string_format_params,
            kwargs,
        )

        return format_string.format(**string_format_kwargs)

    def get_string_format_kwargs(self, string_format_params, kwargs):
        string_format_kwargs = {}

        for key in string_format_params:
            value = kwargs.get(key, KEY_NOT_FOUND)

            assert value != KEY_NOT_FOUND, (
                f"Missing arg `{key}` in kwargs"
            )

            string_format_kwargs[key] = value

        return string_format_kwargs

    def get_string_format_params(self, format_string):
        parse_result = string.Formatter().parse(format_string)

        params = [i for _, i, _, _ in parse_result if i is not None]

        return params

    def get_response(self, method, url, request_kwargs):
        return self.session.request(method, url, **request_kwargs)

    def latest_request_to_curl(self):
        import curlify

        if self.latest_response is None:
            return None

        return curlify.to_curl(self.latest_response.request)

    def get_response_data(self, response):
        response_handler = self.get_response_handler(response)
        response_data = response_handler.handle(response)

        return response_data

    def get_response_handler(self, response):
        response_content_type = self.get_response_content_type(response)
        response_handler_classes = self.get_response_handler_classes()

        for response_handler_class in response_handler_classes:
            response_handler = response_handler_class()

            for content_type in response_handler.get_content_types():

                if content_type in response_content_type:
                    return response_handler

        assert False, (
            f"Unsupported content-type `{response_content_type}` in response"
        )

    def get_response_content_type(self, response):
        return response.headers["content-type"]
    
    def get_response_handler_classes(self):
        return self.response_handler_classes.copy()

    def check_response(self, response, response_data):
        response_status_codes = self.get_response_status_codes()

        if response.status_code not in response_status_codes:
            raise self.ResponseException(
                response=response,
                data=response_data,
            )

    def get_response_status_codes(self):
        assert self.response_status_codes, (
            f"{self.__class__} must define .response_status_codes"
        )

        return self.response_status_codes.copy()

    class ResponseException(Exception):
        
        def __init__(self, response, data, message=None, *args, **kwargs):
            self.response = response
            self.data = data

            if message is None:
                message = (
                    f"{self.response.request.method} "
                    f"{self.response.request.url} "
                    f"{self.response.status_code}\n"
                    f"{self.data}"
                )

            super().__init__(message, *args, **kwargs)

        def to_curl(self):
            import curlify
            
            return curlify.to_curl(self.response.request)
