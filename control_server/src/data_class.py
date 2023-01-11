from __future__ import annotations
from typing import Any, Callable
from abc import ABC


def _is_filtered(
        prop_name: str,
        prop_filter: Callable[[str], bool] = None,
        ignore_props: set[str] = None
):
    if prop_filter is not None and not prop_filter(prop_name):
        return False

    if ignore_props is not None and prop_name in ignore_props:
        return False

    return True


class DataClass(ABC):
    """
    Abstract class that provides functionality to load settings, currently
    using decouple.
    """

    def __init__(self):
        pass

    def __str__(self):
        """
        Generate a string representation of the class, mainly used for
        debugging purposes.
        :return: A string representation of the class.
        """
        outputs = []
        for property_name in self.get_properties():
            outputs.append(
                f"{property_name}: {str(getattr(self, property_name))}"
            )

        return ", ".join(outputs)

    def get_properties(self):
        """
        Get a list of properties in the class.
        :return: A list of tuples, where each tuple contains the name of the
        property, and its type.
        """
        return [(key, type(value)) for (key, value) in vars(self).items()]

    @staticmethod
    def _load_from_dict(
            instance: DataClass,
            data_dict: dict,
            raise_error: bool = True
    ):
        """
        Load data from a dictionary, and set the properties of the class
        accordingly.
        :param instance: An instance of the data class to load the data into.
        :param data_dict: The dictionary to load data from.
        :param raise_error: Whether to raise an error if a property is missing,
        or if types mismatch.
        :return: Whether the data was loaded successfully.
        """
        return instance.load_from(
            lambda prop: data_dict[prop] if prop in data_dict else None,
            raise_error=raise_error
        )

    @staticmethod
    def _try_load_from_dict(
            instance: DataClass,
            data_dict: dict,
            raise_error: bool = True
    ):
        """
        Try to load data from a dictionary, and set the properties of the class
        accordingly. If an error occurs, None is returned.
        :param instance: An instance of the data class to load the data into.
        :param data_dict: The dictionary to load data from.
        :param raise_error: Whether to raise an error if a property is missing.
        :return: The class instance if it was loaded successfully, or None
        otherwise.
        """
        return instance if \
            DataClass._load_from_dict(
                instance,
                data_dict,
                raise_error=raise_error
            ) \
            else None

    def _load_data(
            self,
            data_reader: Callable[[str, type], Any],
            validate_types: bool = False,
            raise_error: bool = True,
            prop_filter: Callable[[str], bool] = None
    ):
        """
        Load data from a data reader, and set the properties of the class
        accordingly.
        :param data_reader: The data reader to use. The data reader should
        provide a value for a given property name and type.
        :param validate_types: Whether to validate that the types of the
        properties matches the types of the values retrieved by the data reader.
        :param raise_error: Whether to raise an error if a property is missing,
        or if types mismatch. Useful to prevent errors from generating when
        handling web requests
        :param prop_filter: A function that takes a property name and returns
        whether the property should be loaded.
        :return: Whether the data was loaded successfully.
        """
        for property_name, property_type in self.get_properties():
            if prop_filter is not None and not prop_filter(property_name):
                continue

            prop_value = data_reader(property_name, property_type)

            if prop_value is None:
                if raise_error:
                    raise ValueError(f'Property "{property_name}" is None')

                return False

            if validate_types and not isinstance(prop_value, property_type):
                if raise_error:
                    raise TypeError(
                        f'Property mismatch: setting "{property_name}" ' +
                        f'is of type "{type(prop_value)}" but "'
                        f'{property_type}" '
                        f'was expected.'
                    )

                return False

        for property_name, property_type in self.get_properties():
            setattr(
                self,
                property_name,
                data_reader(property_name, property_type)
            )

        return True

    def load_from_with_types(
            self,
            data_reader: Callable[[str, type], Any],
            raise_error: bool = True
    ):
        """
        Load data from a data reader that utilizes both property name and type,
        and set the properties of the class accordingly.
        :param data_reader: The data reader to use. The data reader should have
        two arguments: the property name and the property type.
        :param raise_error: Whether to raise an error if a property is missing,
        or if types mismatch.
        :return: Whether the data was loaded successfully.
        """
        return self._load_data(
            data_reader,
            validate_types=True,
            raise_error=raise_error
        )

    def load_from(
            self,
            data_reader: Callable[[str], Any],
            raise_error: bool = True,
            prop_filter: Callable[[str], bool] = None,
            ignore_props: set[str] = None
    ):
        """
        Load data from a data reader that only utilizes property name, and set
        the properties of the class accordingly.
        :param ignore_props: A set of properties to ignore.
        :param data_reader: The data reader to use. The data reader should
        only have one argument: the property name.
        :param raise_error: Whether to raise an error if a property is missing.
        :param prop_filter: A function that takes a property name and returns
        whether the property should be loaded.
        :return: Whether the data was loaded successfully.
        """
        return self._load_data(
            (lambda prop, prop_type: data_reader(prop)),
            validate_types=False,
            raise_error=raise_error,
            prop_filter=lambda prop_name: _is_filtered(
                prop_name,
                prop_filter=prop_filter,
                ignore_props=ignore_props
            )
        )
