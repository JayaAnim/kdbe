from .serializer import Serializer
from .deserializer import Deserializer
import datetime
import decimal

test_dict = {
    "decimal": decimal.Decimal(3.50),
    "now": datetime.datetime.now(),
    "message": "hey there",
    "float": 1.2345,
    "int": 1,
    "bool": False,
    "null": None,
    }
test_list = [test_dict, test_dict, test_dict]
test_tuple = (test_dict, test_dict, test_dict)

s = Serializer()

result = s.serialize(test_dict)
result = s.serialize(test_list)
result = s.serialize(test_tuple)
print(result)

print("")

d = Deserializer()

result = d.deserialize(result)
print(result)
print(type(result))
