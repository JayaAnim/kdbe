from json import JSONEncoder
import decimal
import datetime


class Encoder(JSONEncoder):
    SERIALIZE_METHOD_NAME = "serialize"
    DECIMAL_TYPES = (
        decimal.Decimal,
        )
    DATETIME_TYPES = (
        datetime.datetime,
        datetime.date,
        datetime.time,
        )

    def default(self,obj):
        serialize = getattr(obj,self.SERIALIZE_METHOD_NAME,None)
        if callable(serialize):
            return serialize()

        if isinstance(obj,self.DECIMAL_TYPES):
            return self.handleDecimal(obj)

        if isinstance(obj,self.DATETIME_TYPES):
            return self.handleDatetime(obj)
        
        return super().default(obj)

    def handleDecimal(self,obj):
        return str(obj)

    def handleDatetime(self,obj):
        return obj.isoformat()
