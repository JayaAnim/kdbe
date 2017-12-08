from .serializer import Serializer
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
print(result)
result = s.serialize(test_list)
print(result)
result = s.serialize(test_tuple)
print(result)
