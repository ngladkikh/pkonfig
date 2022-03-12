from pkonfig.base import TypedParameter


class IntParam(TypedParameter):
    def cast(self, string_value: str) -> int:
        return int(string_value)


class FloatParam(TypedParameter):
    def cast(self, string_value: str) -> float:
        return float(string_value)


class StrParam(TypedParameter):
    def cast(self, string_value: str) -> str:
        return string_value
