

class ManagerBase:

    def __init__(self, object_list):
        self.object_list = object_list
        self.index_dict = {}

    def add(self, obj):
        for index_key, index in self.index_dict.items():
            self.add_to_index(index, obj, index_key)
        self.object_list.append(obj)

    def get(self, **kwargs):
        filter_result = self.filter(**kwargs)
        result_count = len(filter_result)

        if result_count > 1:
            raise self.QueryException("query returned more than 1 result. it returned {0}".format(result_count))
        if result_count < 1:
            raise self.NotFoundException("no objects found")

        return filter_result[0]

    def count(self, **kwargs):
        return len(self.filter(**kwargs))

    def filter(self, **kwargs):
        filter_result = None

        for key, value in kwargs.items():

            if key not in self.index_dict:
                self.index(key)

            index = self.index_dict.get(key)
            result = index.get(value, [])

            if filter_result is None:
                filter_result = result
            else:
                filter_result = self.intersection(filter_result, result)

            if not filter_result:
                break
        
        if filter_result is None:
            return self.object_list.copy()

        return filter_result

    def intersection(self, list_1, list_2):
        """
        Returns the intersection
        """
        return [o for o in list_1 if o in list_2]

    def index(self, key):
        #Make sure we haven't indexed by this key yet
        if key in self.index_dict:
            raise self.IndexException(f"key `{key}` has already been indexed")

        self.index_dict[key] = self.make_index(self.object_list, key)

    def make_index(self, object_list, key):
        new_index = {}

        for obj in object_list:
            self.add_to_index(new_index, obj, key)

        return new_index

    def add_to_index(self, index, obj, key):
        value = self.get_value(obj, key)
        value_list = index.get(value, [])
        value_list.append(obj)
        index[value] = value_list
        
    def get_value(self, obj, key):
        """
        Takes an object and a key
        Accesses object at key
        Returns value of object at key
        """
        raise NotImplementedError

    class IndexException(Exception):
        pass

    class QueryException(Exception):
        pass

    class NotFoundException(Exception):
        pass


class DictManager(ManagerBase):

    def get_value(self, obj, key):
        return obj[key]


class ObjectManager(ManagerBase):

    def get_value(self, obj, key):
        return getattr(obj, key)
