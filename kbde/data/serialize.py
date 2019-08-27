

class Serializable:
    serialize_fields = []

    def serialize(self):
        """
        Returns a serializable version of self

        By default, returns the values and keys associated with
        self.serialize_fields
        """
        assert serialize_fields, ("must set self.serialize_fields or override the self.serialize() "
                                  "method")

        return {key:getattr(self, key) for key in self.serialize_fields}
