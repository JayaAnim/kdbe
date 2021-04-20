

class Transformer:

    def transform(self, object_list):
        
        for obj in object_list:
            yield self.transform_object(obj)

    def transform_object(self, obj):
        raise NotImplementedError(
            f"{self.__class__} must implement .transform_object()"
        )


class KeyMapTransformer(Transformer):
    key_map = {}

    def transform_object(self, obj):
        return {
            self.key_map.get(key, key): value for key, value in obj.items()
        }


class KeyReplaceTransformer(Transformer):
    old = None
    new = None

    def __init__(self, *args, **kwargs):
        assert self.old is not None and self.new is not None
        super().__init__(*args, **kwargs)

    def transform_object(self, obj):
        return {
            key.replace(self.old, self.new): value for key, value in obj.items()
        }
