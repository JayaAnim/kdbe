

class Field:
    ems_version = None
    item_number = None
    group_name = None
    subgroup_name = None
    field_name = None
    cieca_field_name = None
    data_type = None
    ems_code_list = None
    description = None
    kbde_field_name = None

    @classmethod
    def from_dbf_record(cls, record):
        field = cls()
        field_name = field.get_cieca_field_name()
        value = record[field_name]
        field.value = value

        return field
    
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __str__(self):
        return self.get_value()

    def get_ems_version(self):
        assert self.ems_version is not None, (
            f"{self.__class__} must define .ems_version"
        )

        return self.ems_version

    def get_item_number(self):
        assert self.item_number is not None, (
            f"{self.__class__} must define .item_number"
        )

        return item_number

    def get_group_name(self):
        assert self.group_name is not None, (
            f"{self.__class__} must define .group_name"
        )

        return self.group_name

    def get_subgroup_name(self):
        assert self.subgroup_name is not None, (
            f"{self.__class__} must define .subgroup_name"
        )

        return self.subgroup_name
    
    def get_field_name(self):
        assert self.field_name is not None, (
            f"{self.__class__} must define .field_name"
        )

        return self.field_name

    def get_cieca_field_name(self):
        assert self.cieca_field_name is not None, (
            f"{self.__class__} must define .cieca_field_name"
        )

        return self.cieca_field_name

    def get_data_type(self):
        assert self.data_type is not None, (
            f"{self.__class__} must define .data_type"
        )

        return self.data_type

    def get_ems_code_list(self):
        return self.ems_code_list.copy()

    def get_description(self):
        assert self.description is not None, (
            f"{self.__class__} must define .description"
        )

    def get_kbde_field_name(self):
        assert self.kbde_field_name is not None, (
            f"{self.__class__} must define .kbde_field_name"
        )

        return self.kbde_field_name

    def get_value(self):
        return self.value
