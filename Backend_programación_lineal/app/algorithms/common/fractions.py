from fractions import Fraction


def to_fraction(value):
    """Convert supported numeric input to an exact rational value."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, float):
        return Fraction(str(value))
    return Fraction(value)