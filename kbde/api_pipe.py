from .api_client import ApiClient


class ApiPipe(ApiClient):
    """
    Reads all data from an api resource and posts each object to a destination resource
    """
    DESTINATION_BASE_PATH = None
    DESTINATION_OBJECT_NAME = None
    DESTINATION_LIST_OBJECT_NAME = None
    CHUNK_SIZE = 100
    OFFSET_PARAMETER = "offset"
    LIMIT_PARAMETER = "limit"
    DESTINATION_OFFSET_PARAMETER = "offset"
    DESTINATION_LIMIT_PARAMETER = "limit"
    ID_ATTRIBUTE = "id"
    DESTINATION_ID_ATTRIBUTE = "id"
    NO_CLEAR = True

    def __init__(self,destination_username=None,
                      destination_password="",
                      destination_api_key=None,
                      *args,
                      **kwargs):
        if self.DESTINATION_BASE_PATH is None:
            raise Exception("no self.DESTINATION_BASE_PATH")
        if self.DESTINATION_OBJECT_NAME is None:
            raise Exception("no self.DESTINATION_OBJECT_NAME")

        ApiClient.__init__(self,*args,**kwargs)

        class DestinationApiClient(ApiClient):
            BASE_PATH = self.DESTINATION_BASE_PATH
            OBJECT_NAME = self.DESTINATION_OBJECT_NAME
        self.destination_client = DestinationApiClient(username=destination_username,
                                                       password=destination_password,
                                                       api_key=destination_api_key)

        if self.DESTINATION_LIST_OBJECT_NAME is not None:
            class DestinationListApiClient(ApiClient):
                BASE_PATH = self.DESTINATION_BASE_PATH
                OBJECT_NAME = self.DESTINATION_LIST_OBJECT_NAME
            self.destination_list_client = DestinationListApiClient(username=destination_username,
                                                                    password=destination_password,
                                                                    api_key=destination_api_key)
        else:
            self.destination_list_client = None

        self.result_id_list = []

    def transfer(self,**kwargs):
        #Get initial data
        offset = 0
        kwargs[self.LIMIT_PARAMETER] = self.CHUNK_SIZE
        kwargs[self.OFFSET_PARAMETER] = offset
        response = self.get(**kwargs)
        data = self.getData(response)
        while data:
            for obj in data:
                result = self.destination_client.post(**obj)
                if "exceptions" in result:
                    self.handleException(obj,result)
                else:
                    result_id = self.getResultId(result)
                    if result_id is not None:
                        self.result_id_list.append(result_id)
                    self.handleSuccess(obj,result)
            offset += self.CHUNK_SIZE
            kwargs[self.OFFSET_PARAMETER] = offset
            response = self.get(**kwargs)
            data = self.getData(response)

    def deleteStale(self,**kwargs):
        if not self.result_id_list:
            """
            There were no items transferred. This could mean that there was a configuration issue, or that the source database was empty. If this did not return, then all data would be deleted out of the destination database. If this is the case, then the destination database should be cleared manually.
            """
            if self.NO_CLEAR:
                return None

        offset = 0
        kwargs[self.DESTINATION_LIMIT_PARAMETER] = self.CHUNK_SIZE
        kwargs[self.DESTINATION_OFFSET_PARAMETER] = offset
        data = self.destination_list_client.get(**kwargs)
        data = self.getDestinationData(data)
        while data:
            for obj in data:
                obj_id = obj.get(self.DESTINATION_ID_ATTRIBUTE)
                #Check to see if this id is in self.result_id_list
                if obj_id in self.result_id_list:
                    continue
                #Delete the object
                delete_args = self.getDeleteArgs(obj)
                delete_args.update(kwargs)
                self.destination_client.delete(**delete_args)
            offset += self.CHUNK_SIZE
            kwargs[self.DESTINATION_OFFSET_PARAMETER] = offset
            data = self.destination_list_client.get(**kwargs)
            data = self.getDestinationData(data)
        
    def getData(self,data):
        """
        Pulls out list of objects from data and returns it
        """
        return data

    def getDestinationData(self,data):
        return data

    def getResultId(self,obj):
        if obj is None:
            return None
        return obj.get(self.DESTINATION_ID_ATTRIBUTE)

    def getDeleteArgs(self,obj):
        obj_id = obj.get(self.DESTINATION_ID_ATTRIBUTE)
        return {"id": obj_id}

    def handleSuccess(self,obj,result):
        return None

    def handleException(self,obj,result):
        print(result["exceptions"])

    def mirror(self,transfer_args={},delete_args={}):
        if self.destination_list_client is None:
            raise Exception("cannot call .mirror() unless self.DESTINATION_LIST_OBJECT_NAME is defined")
        self.transfer(**transfer_args)
        self.deleteStale(**delete_args)
