import datetime
import decimal


class TypeDeserializer:
    EXCEPTIONS = None
    TYPE = None

    def __init__(self,parent_deserializer=None):
        if self.EXCEPTIONS is None:
            raise Exception("self.EXCEPTIONS should be an iterable of exceptions that are expected if the deserialization fails")
        if self.TYPE is None:
            raise Exception("self.TYPE should be the expected type returned from the deserializer")

        self.parent_deserializer = parent_deserializer
        self.parent_deserialize = self.parent_deserializer.deserialize

        self.exception_tuple = self.getExceptionTuple()
        if not isinstance(self.exception_tuple,tuple):
            raise Exception("self.getExceptionTuple() did not return a tuple")

        self.type = self.getType()

    def run(self,data):
        try:
            data = self.deserialize(data)
        except self.exception_tuple as e:
            raise self.CouldNotDeserialize(e)
        assert isinstance(data,self.type)
        return data

    def deserialize(self,data):
        """
        Should return deserialized version of `data`
        """
        raise NotImplementedError

    def getExceptionTuple(self):
        return tuple([e for e in self.EXCEPTIONS])

    def getType(self):
        return self.TYPE

    class CouldNotDeserialize(Exception):
        pass


class ListDeserializer(TypeDeserializer):
    EXCEPTIONS = ()
    TYPE = list

    def deserialize(self,data):
        if isinstance(data,str):
            raise self.CouldNotDeserialize("passed in string")
        if not hasattr(data,"__iter__"):
            raise self.CouldNotDeserialize("was not iterable")
        return [self.parent_deserialize(item) for item in data]


class DictionaryDeserializer(TypeDeserializer):
    EXCEPTIONS = ()
    TYPE = dict

    def deserialize(self,data):
        if not isinstance(data,dict):
            raise self.CouldNotDeserialize("was not a dict")
        new_data = {}
        for key,value in data.items():
            new_data[key] = self.parent_deserialize(value)
        return new_data


class DecimalDeserializer(TypeDeserializer):
    EXCEPTIONS = (
        decimal.InvalidOperation,
        )
    TYPE = decimal.Decimal

    def deserialize(self,data):
        if not isinstance(data,str):
            raise self.CouldNotDeserialize("was not string")
        if "." not in data:
            raise self.CouldNotDeserialize("had no decimal point")
        return decimal.Decimal(data)

class DatetimeDeserializer(TypeDeserializer):
    EXCEPTIONS = (
        ValueError,
        OverflowError,
        )
    TYPE = datetime.datetime
    DATETIME_STRING = "%Y-%m-%dT%H:%M:%S"
    MICROSECOND_STRING = ".%f"
    TIMEZONE_STRING = "%z"
    FORMAT_SUFFIX_LIST = [
        MICROSECOND_STRING + TIMEZONE_STRING,
        MICROSECOND_STRING,
        TIMEZONE_STRING,
        "",
        ]

    def deserialize(self,data):
        if not isinstance(data,str):
            raise self.CouldNotDeserialize("was not a string")
        if len(data) < len(self.DATETIME_STRING):
            raise self.CouldNotDeserialize("not long enough to be datetime")

        time = self.matchTime(data)
        if time is not None:
            return time

        #Try removing the colon from the timezone
        if data[-3] == ":":
            fixed_data = data[:-3] + data[-2:]
            time = self.matchTime(fixed_data)
            if time is not None:
                return time

        raise self.CouldNotDeserialize("was not proper datetime string")

    def matchTime(self,data):
        for format_suffix in self.FORMAT_SUFFIX_LIST:
            time_format = self.DATETIME_STRING + format_suffix
            time = self.getTime(data,time_format)
            if time is not None:
                return time
        return None

    def getTime(self,time,time_format):
        try:
            return datetime.datetime.strptime(time,time_format)
        except ValueError:
            return None


class Deserializer:
    DESERIALIZERS = (
        DatetimeDeserializer,
        DecimalDeserializer,
        DictionaryDeserializer,
        ListDeserializer,
        )

    def __init__(self):
        if not self.DESERIALIZERS:
            raise Exception("no deserializers found in self.DESERIALIZERS")

        self.deserializer_instance_list = self.getDeserializerInstanceList()

    def deserialize(self,data):
        for deserializer in self.deserializer_instance_list:
            try:
                return deserializer.run(data)
            except TypeDeserializer.CouldNotDeserialize as e:
                continue
        return data        

    def getDeserializerInstanceList(self):
        deserializer_instance_list = []
        for TypeDeserializer in self.DESERIALIZERS:
            deserializer = TypeDeserializer(self)
            deserializer_instance_list.append(deserializer)
        return deserializer_instance_list
