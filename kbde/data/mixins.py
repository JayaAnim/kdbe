

class Serialize:
    serialize_fields = None

    def serialize(self):
        """
        Returns a serializable version of self

        By default, returns the values and keys associated with
        self.serialize_fields
        """
        assert self.serialize_fields is not None, (f"{self.__class__.__name__} must set self.serialize_fields or override the `serialize()` method")

        return {key:getattr(self, key) for key in self.serialize_fields}
