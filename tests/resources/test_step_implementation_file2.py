from tests.mock_models import WrappedInt, WrappedString


def int_to_str(i: WrappedInt) -> WrappedString:
    return WrappedString(a_string=str(i.a_int))
