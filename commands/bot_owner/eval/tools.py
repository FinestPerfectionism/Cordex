from collections.abc import Awaitable, Callable
from inspect import isclass, iscoroutinefunction, signature
from typing import Protocol, runtime_checkable

from bot import ContextOrInteraction
from core.responses import format_send
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

        sig = signature(class_object)
        params = list(sig.parameters.values())

        if params and params[0].name in {"self", "cls"}:
            sig = sig.replace(parameters = params[1:])

        return (
            f"{prefix} {name}{brackets}{parent_str}:\n"
            f"    def __init__{sig}"
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

        target_signature = signature(function_object)
        return f"{prefix} {name}{brackets}{target_signature}"

    error = f"Expected class or callable, got {type(target).__name__}"
    raise TypeError(error)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# catch
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def catch[R](
    target : ContextOrInteraction,
    func   : Callable[[ContextOrInteraction], Awaitable[R]],
    /,
) -> R | None:
    try:
        return await func(target)
    except Exception as e:
        await format_send(
            target,
            msg_type = "error",
            title    = "Error! :[",
            subtitle = codeblock(f"{e}"),
            override = True,
        )
        return None
