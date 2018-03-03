from json import JSONEncoder


class Encoder(JSONEncoder):
    TO_JSON_METHOD_NAME = "to_json"

    def default(self,obj):
        to_json = getattr(obj,self.TO_JSON_METHOD_NAME,None)
        if callable(to_json):
            return to_json()
        else:
            return super().default(obj)
