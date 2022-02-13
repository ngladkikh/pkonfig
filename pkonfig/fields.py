from pkonfig.base import TypedParameter


class IntParam(TypedParameter):
    def cast(self, string_value: str):
        return int(string_value)


class FloatParam(TypedParameter):
    def cast(self, string_value: str):
        return float(string_value)


class StrParam(TypedParameter):
    def cast(self, string_value: str):
        return string_value
