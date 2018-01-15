try:
    import requests
except ImportError:
    raise Exception("must install `requests`")

import json
import time
import urllib
from ..data import Deserializer, Serializer

from requests.exceptions import ConnectionError

deserializer = Deserializer()
serializer = Serializer()


class ApiClient:
    BASE_PATH = None
    OBJECT_NAME = None
    API_KEY_PARAMETER = "api_key"
    MAX_RETRIES = 3

    def __init__(self,username=None,password="",api_key=None):
        if self.BASE_PATH is None:
            raise Exception("no self.BASE_PATH")
        if self.OBJECT_NAME is None:
            raise Exception("no self.OBJECT_NAME")

        self.api_key = api_key
        self.session = self.makeSession(username,password)

    def makeSession(self,username,password):
        session = requests.Session()
        if username is not None:
            session.auth = (username,password)
        return session

    def get(self,*path_list,**parameter_dict):
        url = self.makeUrl(*path_list,**parameter_dict)
        return self.makeRequest(self.session.get,url)

    def post(self,*path_list,**parameter_dict):
        url = self.makeUrl(*path_list)
        return self.makeRequest(self.session.post,url,parameter_dict)

    def put(self,*path_list,**parameter_dict):
        url = self.makeUrl(*path_list)
        return self.makeRequest(self.session.put,url,parameter_dict)
        
    def delete(self,*path_list,**parameter_dict):
        url = self.makeUrl(*path_list,**parameter_dict)
        return self.makeRequest(self.session.delete,url)

    def makeUrl(self,*path_list,**query_dict):
        #Add the api_key
        if self.api_key:
            query_dict[self.API_KEY_PARAMETER] = self.api_key
        return makeUrl(self.BASE_PATH,self.OBJECT_NAME,*path_list,**query_dict)

    def makeRequest(self,request_function,url,data=None):
        kwargs = {}
        if data is not None:
            for key,value in data.items():
                value = serializer.serialize(value)
                value = json.dumps(value)
                data[key] = value
            kwargs['data'] = data

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
                    if attempt_count >= self.MAX_RETRIES:
                        raise self.ServerException("service unavailable")
                    else:
                        #Try again
                        time.sleep(attempt_count)
                        continue

                break

            except ConnectionError as e:
                if attempt_count >= self.MAX_RETRIES:
                    raise self.ConnectionException("could not connect")
                #Wait, then retry the request
                time.sleep(attempt_count)

        try:
            response_data = self.loadData(response.text)
        except ValueError:
            raise self.ResponseException("could not parse response")

        return response_data

    def loadData(self,data):
        data = json.loads(data)
        data = deserializer.deserialize(data)
        return data


    class ConnectionException(Exception):
        pass

    class NotFoundException(Exception):
        pass

    class ServerException(Exception):
        pass

    class ResponseException(Exception):
        pass



def makeUrl(*path_list,**query_dict):
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
