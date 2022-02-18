from pkonfig.base import TypedParameter


class IntParam(TypedParameter):
    returns = int

    def cast(self, string_value: str):
        return int(string_value)


class FloatParam(TypedParameter):
    returns = float

    def cast(self, string_value: str):
        return float(string_value)


class StrParam(TypedParameter):
    returns = str

    def cast(self, string_value: str):
        return string_value
