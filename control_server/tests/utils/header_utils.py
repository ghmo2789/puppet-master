from typing import Any, Callable

from control_server.src.middleware.headers.byte_convertible import \
    ByteConvertible


class HeaderUtils:
    def __init__(
            self,
            convertible_creator: Callable[[], ByteConvertible]
    ):
        self.convertible_creator = convertible_creator

    @staticmethod
    def _assert_write_props(
            convertible: ByteConvertible,
            data: dict[str, Any]):
        for prop_name, prop in convertible.serialized_properties.items():
            assert prop_name in data, \
                f'Property {prop_name} not in provided data, but is in ' \
                f'provided convertible class instances serialized properties.'

            convertible.write_prop(prop, data[prop_name])

    @staticmethod
    def _assert_read_props(
            convertible: ByteConvertible,
            data: dict[str, Any]):
        for prop_name, prop in convertible.serialized_properties.items():
            assert prop_name in data, \
                f'Property {prop_name} not in provided data, but is in ' \
                f'provided convertible class instances serialized properties.'

            assert convertible.read_prop(prop) == data[prop_name], \
                f'Property {prop_name} has value {prop.read()}, but expected ' \
                f'value {data[prop_name]}.'

    def assert_read(
            self,
            data: bytes,
            expected: dict[str, Any]):
        convertible = self.convertible_creator()
        convertible.load_from_bytes(data)
        HeaderUtils._assert_read_props(convertible, expected)

    def assert_write(
            self,
            expected: bytes,
            data: dict[str, Any]):
        convertible = self.convertible_creator()

        HeaderUtils._assert_write_props(convertible, data)

        assert convertible.to_bytes() == expected, \
            f'Expected bytes {expected}, but got {convertible.to_bytes()}.'

    def assert_read_write(
            self,
            data: dict[str, Any],
            expected: dict[str, Any] = None):
        convertible = self.convertible_creator()
        HeaderUtils._assert_write_props(convertible, data)
        read_bytes = convertible.to_bytes()

        other_convertible = self.convertible_creator()
        other_convertible.load_from_bytes(read_bytes)
        HeaderUtils._assert_read_props(other_convertible, data)