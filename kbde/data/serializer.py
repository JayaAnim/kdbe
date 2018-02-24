import inspect

import datetime
import decimal


class TypeSerializer:
    TYPES = None

    def __init__(self,parent_serializer=None):
        if self.TYPES is None:
            raise Exception("self.TYPES should be an iterable containing this serializer's supported types")

        self.parent_serializer = parent_serializer
        self.parent_serialize = self.parent_serializer.serialize

        self.type_tuple = self.getTypeTuple()
        if not isinstance(self.type_tuple,tuple):
            raise Exception("self.getTypeTuple() did not return a tuple")

    def run(self,data):
        assert isinstance(data,self.TYPES)
        return self.serialize(data)

    def serialize(self,data):
        """
        Should return the serialized version of `data`
        """
        raise NotImplementedError

    def getTypeTuple(self):
        return tuple([t for t in self.TYPES])


class ListSerializer(TypeSerializer):
    TYPES = (
        list,
        tuple,
        set,
        range,
        frozenset,
        )

    def serialize(self,data_list):
        return [self.parent_serialize(data) for data in data_list]


class DatetimeSerializer(TypeSerializer):
    TYPES = (
        datetime.datetime,
        datetime.date,
        datetime.time,
        )

    def serialize(self,time):
        return time.isoformat()


class DecimalSerializer(TypeSerializer):
    TYPES = (
        decimal.Decimal,
        )

    def serialize(self,data):
        return str(data)


class DictionarySerializer(TypeSerializer):
    TYPES = (
        dict,
        )

    def serialize(self,data):
        result = {}
        for key,value in data.items():
            result[key] = self.parent_serialize(value)
        return result


class BytesSerializer(TypeSerializer):
    TYPES = (
        bytes,
        )

    def serialize(self,data):
        return data.decode("utf-8")


class Serializer:
    SERIALIZERS = (
        ListSerializer,
        DatetimeSerializer,
        DecimalSerializer,
        DictionarySerializer,
        BytesSerializer,
        )

    def __init__(self):
        if not self.SERIALIZERS:
            raise Exception("no serializers found in self.SERIALIZERS")

        self.serializer_instance_list = self.getSerializerInstanceList()

    def serialize(self,data):
        #If item is a class and not an instance, return None
        if inspect.isclass(data):
            return None

        for serializer in self.serializer_instance_list:
            if isinstance(data,serializer.type_tuple):
                return serializer.run(data) 

        if hasattr(data,"__dict__"):
            return self.serialize(data.__dict__)

        return data

    def getSerializerInstanceList(self):
        serializer_instance_list = []
        for TypeSerializer in self.SERIALIZERS:
            serializer = TypeSerializer(self)
            serializer_instance_list.append(serializer)
        return serializer_instance_list
