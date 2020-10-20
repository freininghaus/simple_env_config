class EnvironmentVariableNotFoundError(KeyError):
    def __init__(self, class_name: str, attribute_name: str, attribute_type: type):
        self.class_name = class_name
        self.attribute_name = attribute_name
        self.attribute_type = attribute_type

        super().__init__(f"class '{self.class_name}' expects a value of type {self.attribute_type} "
                         f"in the environment variable '{self.attribute_name}'")


class CannotConvertEnvironmentVariableError(ValueError):
    def __init__(self, class_name: str, attribute_name: str, attribute_value: str, attribute_type: type, details: str):
        self.class_name = class_name
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.attribute_type = attribute_type
        self.details = details

        super().__init__(f"class '{self.class_name}' expects a value of type {self.attribute_type} "
                         f"in the environment variable '{self.attribute_name}', but the value '{self.attribute_value}' "
                         f"could not be converted: {self.details}")


class CanOnlyDecorateClassesError(ValueError):
    pass
