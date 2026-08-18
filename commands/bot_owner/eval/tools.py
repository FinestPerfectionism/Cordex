from inspect import isclass, iscoroutinefunction, signature
from typing import Protocol, runtime_checkable

from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Tools
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# show_def
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@runtime_checkable
class HasName(Protocol):
    __name__ : str

@runtime_checkable
class HasTypeParams(Protocol):
    __type_params__ : tuple[object, ...]

def show_def(target : object, /) -> str:
    if isclass(target):
        prefix = "class"

        class_object = target
        name         = class_object.__name__

        brackets        = ""
        type_parameters = class_object.__type_params__

        if type_parameters:
            class_parameter_names = [parameter.__name__ for parameter in type_parameters]
            brackets              = f"[{', '.join(class_parameter_names)}]"

        bases      = [
            base.__name__
            for base in class_object.__bases__
            if base is not object
        ]
        parent_str = f"({', '.join(bases)})" if bases else ""

        sig    = signature(class_object, eval_str = True)
        params = list(sig.parameters.values())

        if params and params[0].name in {"self", "cls"}:
            sig = sig.replace(parameters = params[1:])

        standard_sig = str(sig)
        init_prefix  = "    def __init__"

        if len(init_prefix) + len(standard_sig) <= 80:
            formatted_sig = standard_sig
        else:
            parameter_lines = [
                f"        {parameter},"
                for parameter in sig.parameters.values()
            ]
            formatted_sig = f"(\n{'\n'.join(parameter_lines)}\n    )"

        return codeblock(
            (
               f"{prefix} {name}{brackets}{parent_str}:\n"
               f"{init_prefix}{formatted_sig}:\n"
                "        ..."
            ),
        )

    if callable(target):
        function_object = target

        prefix = "async def" if iscoroutinefunction(function_object) else "def"
        name   = "unknown"

        if isinstance(function_object, HasName):
            name = function_object.__name__

        brackets = ""

        if isinstance(function_object, HasTypeParams):
            function_type_parameters = function_object.__type_params__
            if function_type_parameters:
                function_parameter_names = [
                    parameter.__name__ if isinstance(parameter, HasName) else str(parameter)
                    for parameter in function_type_parameters
                ]
                brackets = f"[{", ".join(function_parameter_names)}]"

        target_signature = signature(function_object, eval_str = True)
        standard_sig     = str(target_signature)
        func_prefix      = f"{prefix} {name}{brackets}"

        if len(func_prefix) + len(standard_sig) <= 80:
            formatted_sig = standard_sig
        else:
            parameter_lines = [
                f"    {parameter},"
                for parameter in target_signature.parameters.values()
            ]
            formatted_sig = f"(\n{'\n'.join(parameter_lines)}\n)"

        return codeblock(
            (
               f"{func_prefix}{formatted_sig}:\n"
                "    ..."
            ),
        )

    error = f"Expected class or callable, got {type(target).__name__}"
    raise TypeError(error)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# show_attrs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def show_attrs(target : object, /, *, tall : bool = False, dunders : bool = False) -> str:
    attrs = dir(target)

    if not dunders:
        attrs = [attr for attr in attrs if not attr.startswith("__")]

    joiner = "\n" if tall else ", "

    return codeblock(joiner.join(attrs))
