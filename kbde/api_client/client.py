import requests
import string
from .. import url


class Client:
    # Hostname of the service to which you are connecting
    host = None

    # The path to the resource that you need
    # Allows for string formatters in the path
    # Params in this path will be replaced with values in given params
    path = None

    # Request content types
    CONTENT_TYPE_TEXT = "text"
    CONTENT_TYPE_JSON = "json"
    CONTENT_TYPE_MULTIPART = "multipart"

    # Requests params mapping
    REQUEST_BODY_PARAM_MAP = {
        CONTENT_TYPE_TEXT: "data",
        CONTENT_TYPE_JSON: "json",
        CONTENT_TYPE_MULTIPART: "files",
        }

    request_content_type = CONTENT_TYPE_JSON

    # Headers that will be added to every request
    # Can be templatized strings
    headers = {}

    def __init__(self, username=None, password=None, **params):
        assert self.host is not None, "must define self.host"
        assert self.path is not None, "must define self.path"

        self.session = self.make_session(username, password)
        self.params = params

    def make_session(self, username, password):
        session = requests.Session()

        if username is not None:
            assert password is not None, "you provided a username, but did not provide a password"
            session.auth = (username, password or "")

        return session

    def get(self, **params):
        return self.make_request(self.session.get, params)

    def post(self, **params):
        return self.make_request(self.session.post, params)

    def put(self, **params):
        return self.make_request(self.session.put, params)
        
    def delete(self, **params):
        return self.make_request(self.session.delete, params)

    def make_request(self, function, params):
        params = self.get_merged_params(params)

        headers = self.get_formatted_headers(params)
        url = self.make_url(params)

        # If the request type has a body, get it
        if function in [self.session.post, self.session.put]:
            request_body_params = self.get_request_body_params(params)
        else:
            request_body_params = {}

        kwargs = {
            "headers": headers,
            }

        if function == self.session.get:
            # Add the remaining params to the request call
            kwargs["params"] = params

        # Add the body params
        kwargs.update(request_body_params)

        response = self.call_request_function(function, url, kwargs)

        response_data = self.get_response_data(response)

        return response_data

    def get_merged_params(self, params):
        p = self.get_params()
        p.update(params)
        return p

    def make_url(self, params):
        host = self.get_host(**params)
        path = self.get_path(**params)

        url_path = host + path

        url_path = self.format_string_from_params(url_path, params)

        return url.make_url(url_path)

    def get_request_body_params(self, params):
        """
        Returns the proper arg with values depending on what kind of requests we are sending
        Supports regular params or json
        """
        request_content_type = self.get_request_content_type(**params)

        request_param_key = self.REQUEST_BODY_PARAM_MAP.get(request_content_type)
        assert request_param_key, "request_content_type `{}` not supported".format(request_content_type)

        request_params = {request_param_key: params}

        return request_params

    def get_formatted_headers(self, params):
        headers = self.get_headers(**params)
        assert isinstance(headers, dict)
        for key, value in headers.items():
            headers[key] = self.format_string_from_params(value, params)
        return headers

    def format_string_from_params(self, s, params):
        """
        Gets string format variables from string
        Pops each variable out of params
        Formats string
        """
        assert isinstance(s, str)
        assert isinstance(params, dict)

        format_param_list = self.get_string_format_params(s)

        no_key = object()
        format_params = {}
        for p in format_param_list:
            value = params.pop(p, no_key)
            if value == no_key:
                raise self.ApiClientException("param `{}` was not given to format string `{}`"
                                              "".format(p, s))
            format_params[p] = value

        return s.format(**format_params)

    def get_string_format_params(self, s):
        parse_result = string.Formatter().parse(s)
        params = [i for _, i, _, _ in parse_result if i is not None]
        return params

    def call_request_function(self, function, url, kwargs):
        return function(url, **kwargs)

    def get_response_data(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                response_json = response.json()
                response_json["status_code"] = response.status_code
                raise self.ApiClientException(response_json)
            except ValueError:
                raise e

        if not response._content:
            return None

        # TODO: support other types of responses
        return response.json()

    def get_host(self, **params):
        return self.host

    def get_path(self, **params):
        return self.path

    def get_request_content_type(self, **params):
        return self.request_content_type

    def get_headers(self, **params):
        return self.headers.copy()

    def get_params(self, **params):
        return self.params.copy()

    class ApiClientException(Exception):
        pass
