"Fields management"

# pylint: disable=protected-access

# TOFIX:
# pylint: disable=invalid-name


# from pprint import pprint
from types import SimpleNamespace
from typing import Callable

from superconf import exceptions

from .casts import AsBoolean, AsDict, AsIdentity, AsInt, AsList, AsOption, AsTuple
from .common import FAIL, NOT_SET
from .loaders import _Value

# Shortcuts for standard casts
as_boolean = AsBoolean()
as_int = AsInt()
as_list = AsList()
as_dict = AsDict()
as_tuple = AsTuple()
as_option = AsOption
as_is = AsIdentity()


class Field:
    """Base class for configuration fields.

    A Field represents a single configuration value with optional type casting,
    default values, and help text. Fields are used as descriptors in configuration
    classes to define the structure and behavior of configuration values.

    Attributes:
        cast: The casting function to use for converting raw values. If None,
            will be determined based on the default value's type.
    """

    cast = None

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        key: str = None,
        *,
        help: str = "",
        default=NOT_SET,
        cast: Callable = None,
    ):
        """Initialize a new Field instance.

        Args:
            key: Name of the value used in file or environment variable.
                Set automatically by the metaclass.
            help: Plain-text description of the value.
            default: Default value if none is provided. If left unset,
                loading a config that fails to provide this value
                will raise a UnknownConfiguration exception.
            cast: Callable to cast variable with. Defaults to type of
                default (if provided), identity if default is not
                provided or raises TypeError if provided cast is not
                callable.
        """
        self.key = key
        self.help = help
        self.default = default
        self.cast = cast or self.cast

    def __get__(self, conf_instance, owner):
        """Descriptor get method to retrieve the field's value.

        Args:
            conf_instance: The configuration instance this field belongs to.
            owner: The class that owns this descriptor.

        Returns:
            The field's value if accessed through an instance,
            or the field itself if accessed through the class.
        """
        if conf_instance:
            return conf_instance.get_field_value(key=self.key, field=self)
        return self

    def __repr__(self):
        """Return a string representation of the field.

        Returns:
            A string showing the field's class name, key, and help text.
        """
        return f'{self.__class__.__name__}(key="{self.key}", help="{self.help}")'

    def is_container(self):
        """Check if this field is a container type.

        Returns:
            bool: True if this field has a children_class attribute,
            indicating it can contain nested configuration values.
        """
        children_class = getattr(self, "children_class", None)
        if children_class is not None:
            return True
        return False

    # pylint: disable=too-many-locals, too-many-branches, too-many-arguments, too-many-statements, too-many-positional-arguments
    def resolve_value(
        self,
        conf_instance,
        value=NOT_SET,
        default=NOT_SET,
        cast=NOT_SET,
        loaders=NOT_SET,
        **kwargs,
    ):
        """Resolve the final value for this field.

        This method handles the complex logic of determining the field's value by:
        1. Checking for explicitly provided values
        2. Looking up values through loaders
        3. Falling back to defaults
        4. Applying type casting

        Args:
            conf_instance: The configuration instance this field belongs to.
            value: Explicitly provided value, takes precedence if set.
            default: Override for the field's default value.
            cast: Override for the field's cast function.
            loaders: List of loader objects to use for value lookup.
            **kwargs: Additional keyword arguments passed to loaders.

        Returns:
            tuple: A tuple containing:
                - The resolved and cast value
                - A SimpleNamespace containing metadata about the resolution process

        Raises:
            CastValueFailure: If strict casting is enabled and the value
                cannot be cast to the desired type.
        """
        key = self.key
        assert isinstance(key, (str, int)), f"Got: {type(key)} {key}"

        # Process defaults
        default_from = ["args"]
        if default is NOT_SET and isinstance(conf_instance._default, dict):
            # Fetch default from container

            # default2 = default
            try:
                default = conf_instance.query_inst_cfg(
                    "default", override=kwargs, default=NOT_SET
                )[key]
                default_from.append("conf_instance_query")
            except KeyError:
                pass

        if default is NOT_SET:
            # Fetch default from field
            default = self.default
            default_from.append("field_instance")

        # Process value
        if value is NOT_SET:
            # Fetch default from container
            try:
                value = conf_instance._value[key]
            except (TypeError, KeyError):  # For dict
                pass
            except IndexError:  # For list
                pass

        # Process cast
        cast_from = []
        if cast is NOT_SET:
            cast = self.cast
            cast_from.append(f"field_attr:{self}.cast")
        if cast is NOT_SET:
            cast = conf_instance._cast
            cast_from.append(f"conf_attr:{conf_instance}._cast")

        # Process loaders
        if loaders is NOT_SET:
            loaders = conf_instance._loaders
        if value:
            loaders.insert(0, _Value({key: value}))

        # Determine cast method
        if callable(cast):
            # cast = cast
            cast_from.append("cast_is_callable")
        elif cast is None and (default is NOT_SET or default is None):
            cast = as_is
            cast_from.append("cast_is_none_and_no_defaults")
        elif isinstance(default, bool):
            cast = as_boolean
            cast_from.append("cast_as_boolean")
        elif cast is None:
            cast = type(default)
            cast_from.append("cast_is_none")
        elif cast is NOT_SET:
            if default is NOT_SET or default is None:
                cast_from.append("cast_notset_type_default")
                cast = type(default)
            else:
                cast_from.append("cast_notset_type_as_is")
                cast = as_is
        else:
            raise TypeError(f"Cast must be callable, got: {type(cast)}")

        # Process things
        result = NOT_SET
        loader_from = []
        for loader in loaders:
            loader_from.append(str(loader))
            try:
                # print(f"  > LOADER: try search in {loader} key: {key}")
                result = loader.getitem(self, key, **kwargs)

            except (KeyError, TypeError):
                # print (f"{self}: Loader {key} {loader.__class__.__name__}
                # failed with error: {type(err)}{err}")
                continue

            if result is not NOT_SET:
                result = cast(result)
                break

        # Nothing found in all loaders, then fallback on default
        results_from = []
        if result is NOT_SET:
            result = value
            results_from.append("from_value")
        if result is NOT_SET:
            result = default
            results_from.append("from_default")

        # Try to cast value
        error = None
        try:
            result = cast(result)
            results_from.append(f"casted:{cast}")
        # except ValueError as err:
        #     error = err
        except exceptions.InvalidCastConfiguration as err:
            error = err

        # Check for strict_cast mode:
        # print ("DEFAUUUB", conf_instance, conf_instance._strict_cast)
        if error is not None and conf_instance._strict_cast is True:
            msg = (
                f"Got error {conf_instance}.{key} {type(error)}: {error}, "
                "set strict_cast=False to disable this error"
            )
            raise exceptions.CastValueFailure(msg)

        meta = SimpleNamespace(
            cast=cast,
            default=default,
            loaders=loaders,
            value=result,
            cast_from=cast_from,
            loader_from=loader_from,
            results_from=results_from,
            default_from=default_from,
        )

        return result, meta


class FieldConf(Field):
    """A field that represents a nested configuration.

    This field type allows for hierarchical configuration structures by containing
    another configuration class as its value.

    Attributes:
        children_class: The configuration class to use for nested values.
    """

    def __init__(
        self,
        children_class,
        key: str = None,
        **kwargs,
    ):
        """Initialize a nested configuration field.

        Args:
            children_class: The configuration class to use for nested values.
            key: Name of the value used in file or environment variable.
            **kwargs: Additional arguments passed to the parent Field class.
        """
        super().__init__(key, **kwargs)
        self.children_class = children_class


class FieldBool(Field):
    """A field that stores and validates boolean values.

    Uses the AsBoolean cast to convert various string representations
    to boolean values (e.g., 'yes'/'no', 'true'/'false', '1'/'0').

    Attributes:
        cast: Set to AsBoolean() for automatic type conversion.
    """

    cast = as_boolean


class FieldString(Field):
    """A field that stores string values.

    Ensures values are stored as strings, converting other types
    if necessary using Python's built-in str() function.

    Attributes:
        cast: Set to str for automatic type conversion.
    """

    cast = str


class FieldInt(Field):
    """A field that stores integer values.

    Uses the AsInt cast to convert string representations to integers,
    raising an error if the conversion fails.

    Attributes:
        cast: Set to AsInt() for automatic type conversion.
    """

    cast = as_int


class FieldFloat(Field):
    """A field that stores floating-point values.

    Uses Python's built-in float() function to convert values,
    raising an error if the conversion fails.

    Attributes:
        cast: Set to float for automatic type conversion.
    """

    cast = float


class FieldOption(Field):
    """A field that validates values against a predefined set of options.

    This field ensures that values are one of a predefined set of options,
    optionally providing a default if an invalid option is given.

    Attributes:
        cast: Set to AsOption for option validation and conversion.
    """

    cast = as_option

    def __init__(
        self,
        options,
        default_option=FAIL,
        key: str = None,
        **kwargs,
    ):
        """Initialize an option field.

        Args:
            options: Dictionary mapping valid input values to their corresponding options.
            default_option: The option to use when an invalid value is provided.
                If set to FAIL, raises an error for invalid values.
            key: Name of the value used in file or environment variable.
            **kwargs: Additional arguments passed to the parent Field class.

        Raises:
            AssertionError: If options is not a dictionary.
        """
        assert isinstance(options, dict), f"Expected a dict, got: {options}"
        self.cast = AsOption(options, default_option=default_option)
        super().__init__(key, **kwargs)


class FieldDict(Field):
    """A field that stores dictionary values.

    Uses the AsDict cast to ensure values are proper dictionaries,
    with support for converting mapping objects.

    Attributes:
        cast: Set to AsDict() for automatic type conversion.
    """

    cast = as_dict


class FieldList(Field):
    """A field that stores list values.

    Uses the AsList cast to convert various inputs to lists, including:
    - Comma-separated strings
    - Other sequence types
    - Empty values to empty lists

    Attributes:
        cast: Set to AsList() for automatic type conversion.
    """

    cast = as_list


class FieldTuple(Field):
    """A field that stores tuple values.

    Uses the AsTuple cast to convert various inputs to tuples, including:
    - Comma-separated strings
    - Other sequence types
    - Empty values to empty tuples

    Attributes:
        cast: Set to AsTuple() for automatic type conversion.
    """

    cast = as_tuple


# Compatibility with classyconf
Value = Field  # Alias for backward compatibility
