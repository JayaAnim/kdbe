import requests
import json
import time
import urllib
import io

from requests import exceptions as requests_exceptions


class ApiClient:
    base_path = None
    object_name = None
    api_key_parameter = "api_key"
    max_retries = 3

    def __init__(self,username=None,password="",api_key=None):
        if self.base_path is None:
            raise Exception("no self.base_path")
        if self.object_name is None:
            raise Exception("no self.object_name")

        self.api_key = api_key
        self.session = self.make_session(username,password)

    def make_session(self,username,password):
        session = requests.Session()
        if username is not None:
            session.auth = (username,password)
        return session

    def get(self,*path_list,**parameter_dict):
        url = self.make_url(*path_list,**parameter_dict)
        return self.make_request(self.session.get,url)

    def post(self,*path_list,**parameter_dict):
        url = self.make_url(*path_list)
        return self.make_request(self.session.post,url,parameter_dict)

    def put(self,*path_list,**parameter_dict):
        url = self.make_url(*path_list)
        return self.make_request(self.session.put,url,parameter_dict)
        
    def delete(self,*path_list,**parameter_dict):
        url = self.make_url(*path_list,**parameter_dict)
        return self.make_request(self.session.delete,url)

    def make_url(self,*path_list,**query_dict):
        #Add the api_key
        if self.api_key:
            query_dict[self.api_key_parameter] = self.api_key
        return make_url(self.base_path,self.object_name,*path_list,**query_dict)

    def make_request(self,request_function,url,data=None):
        kwargs = {}
        if data is not None:
            #Serialize each field in the data
            new_data = {}
            files = {}
            for key,value in data.items():
                if isinstance(value,io.IOBase):
                    files[key] = value
                    continue

                value = json.dumps(value)
                new_data[key] = value
            #Feed the data into multipart form
            kwargs["data"] = new_data
            kwargs["files"] = files

        attempt_count = 0
        while True:
            attempt_count += 1
            try:
                response = request_function(url,**kwargs)

                #Check to make sure that the resource was found
                if response.status_code == 404:
                    raise self.NotFoundException("could not find resource {0}".format(url))

                if response.status_code == 500:
                    raise self.ServerException("internal server error")

                if response.status_code in [502,503]:
                    if attempt_count >= self.max_retries:
                        raise self.ServerException("service unavailable")
                    else:
                        #Try again
                        time.sleep(attempt_count)
                        continue

                break

            except requests_exceptions.ConnectionError as e:
                if attempt_count >= self.max_retries:
                    raise self.ConnectionException("could not connect")
                #Wait, then retry the request
                time.sleep(attempt_count)

        try:
            response_data = self.load_data(response.text)
        except ValueError:
            raise self.ResponseException("could not parse response. status: {0}".format(response.status_code))

        return response_data

    def load_data(self,data):
        data = json.loads(data)
        return data


    class ConnectionException(Exception):
        pass

    class NotFoundException(Exception):
        pass

    class ServerException(Exception):
        pass

    class RequestException(Exception):
        pass

    class ResponseException(Exception):
        pass



def make_url(*path_list,**query_dict):
    #Make path
    path = "/".join(path_list)

    #Make query
    query_dict = {key: query_dict[key] for key in query_dict if query_dict[key] is not None}
    query = urllib.parse.urlencode(query_dict)

    #Make url
    url_list = [path]
    if query:
        url_list.append(query)
    url = "?".join(url_list)

    return url
