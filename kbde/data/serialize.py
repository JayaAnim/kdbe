

class Serializable:
    serialize_fields = []

    def serialize(self):
        """
        Returns a serializable version of self

        By default, returns the values and keys associated with
        self.serialize_fields
        """
        return {key:getattr(self, key) for key in self.serialize_fields}
