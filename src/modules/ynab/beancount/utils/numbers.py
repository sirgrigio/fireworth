from decimal import Decimal
import math


def to_int_or_float(value: str) -> int | float:
    if value is None:
        return None
    return int(value) if '.' not in str(value) else float(value)


def get_precision(value: int | float) -> int:
        max_digits = 14
        int_part = int(abs(value))
        magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
        if magnitude >= max_digits:
            return (magnitude, 0)
        frac_part = abs(value) - int_part
        multiplier = 10 ** (max_digits - magnitude)
        frac_digits = multiplier + int(multiplier * frac_part + 0.5)
        while frac_digits % 10 == 0:
            frac_digits /= 10
        scale = int(math.log10(frac_digits))
        return scale


def to_decimal(value: int | float, precision: int=2) -> Decimal:
    return Decimal(value).quantize(Decimal(10)**-precision)
