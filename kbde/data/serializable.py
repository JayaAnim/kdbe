

class Serializable:
    SERIALIZE_FIELDS = []

    def serialize(self):
        """
        Returns a serializable version of self

        By default, returns the values and keys associated with
        self.SERIALIZE_FIELDS
        """
        return {key:getattr(self,key) for key in self.SERIALIZE_FIELDS}
