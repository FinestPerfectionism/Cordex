from inspect import cleandoc, isclass, iscoroutinefunction, signature
from json import dumps
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
            brackets              = f"[{", ".join(class_parameter_names)}]"

        bases      = [
            base.__name__
            for base in class_object.__bases__
            if base is not object
        ]
        parent_str = f"({", ".join(bases)})" if bases else ""

        sig    = signature(class_object)
        params = list(sig.parameters.values())

        if params and params[0].name in {"self", "cls"}:
            sig = sig.replace(parameters = params[1:])

        standard_sig = str(sig)
        init_prefix  = "    def __init__"

        if len(init_prefix) + len(standard_sig) <= 80:
            formatted_sig = standard_sig
        else:
            lines = []
            parameters = list(sig.parameters.values())
            for i, param in enumerate(parameters):
                lines.append(f"        {param},")
                if param.kind == param.POSITIONAL_ONLY:
                    next_param = parameters[i + 1] if i + 1 < len(parameters) else None
                    if next_param is None or next_param.kind != param.POSITIONAL_ONLY:
                        lines.append("        /,")

                elif param.kind == param.KEYWORD_ONLY:
                    prev_param = parameters[i - 1] if i > 0 else None
                    if prev_param and prev_param.kind not in {param.KEYWORD_ONLY, param.VAR_POSITIONAL}:
                        lines.insert(-1, "        *,")

            formatted_sig = f"(\n{"\n".join(lines)}\n    )"

        docstring = getattr(class_object, "__doc__", None)
        if isinstance(docstring, str) and docstring.strip():
            cleaned        = cleandoc(docstring)
            indented_lines = [f"        {line}" if line else "" for line in cleaned.splitlines()]
            body           = f'        """\n{"\n".join(indented_lines)}\n        """\n'
        else:
            body = ""

        return codeblock(
            (
               f"{prefix} {name}{brackets}{parent_str}:\n"
               f"{init_prefix}{formatted_sig}:\n"
               f"{body}"
                "        ..."
            ),
        )

    if callable(target):
        function_object = target

        prefix = "async def" if iscoroutinefunction(function_object) else "def"

        name = getattr(
            function_object,
            "__name__",
            getattr(getattr(function_object, "__func__", None), "__name__", "unknown"),
        )

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

        standard_sig     = str(target_signature)
        func_prefix      = f"{prefix} {name}{brackets}"

        if len(func_prefix) + len(standard_sig) <= 80:
            formatted_sig = standard_sig
        else:
            lines : list[str] = []
            parameters = list(target_signature.parameters.values())
            for i, param in enumerate(parameters):
                lines.append(f"    {param},")
                if param.kind == param.POSITIONAL_ONLY:
                    next_param = parameters[i + 1] if i + 1 < len(parameters) else None
                    if next_param is None or next_param.kind != param.POSITIONAL_ONLY:
                        lines.append("    /,")

                elif param.kind == param.KEYWORD_ONLY:
                    prev_param = parameters[i - 1] if i > 0 else None
                    if prev_param and prev_param.kind not in {param.KEYWORD_ONLY, param.VAR_POSITIONAL}:
                        lines.insert(-1, "    *,")

            formatted_sig = f"(\n{"\n".join(lines)}\n)"

        docstring = getattr(function_object, "__doc__", None)
        if isinstance(docstring, str) and docstring.strip():
            cleaned        = cleandoc(docstring)
            indented_lines = [f"    {line}" if line else "" for line in cleaned.splitlines()]
            body           = f'    """\n{"\n".join(indented_lines)}\n    """\n'
        else:
            body = ""

        return codeblock(
            (
               f"{func_prefix}{formatted_sig}:\n"
               f"{body}"
                "    ..."
            ),
        )

    error = f"Expected class or callable, got {type(target).__name__}"
    raise TypeError(error)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# show_attrs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def show_attrs(
    target   : object,
    /,
    *,
    tall     : bool | None = None,
    dunders  : bool        = False,
    privates : bool        = False,
) -> str:
    def _filter(attr : str) -> bool:
        if attr.startswith("__") and attr.endswith("__"):
            return dunders
        if attr.startswith("_"):
            return privates
        return True

    attrs = [attr for attr in dir(target) if _filter(attr)]

    if tall is None:
        estimated_length = sum(len(a) for a in attrs) + (2 * (len(attrs) - 1))
        tall = estimated_length > 80

    joiner = ",\n" if tall else ", "

    return codeblock(joiner.join(attrs))

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_dict
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_dict(dictionary : dict[str, object], /, *, indent : int = 4) -> str:
    return codeblock(dumps(dictionary, indent = indent))
