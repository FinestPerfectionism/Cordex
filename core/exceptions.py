from discord import app_commands
from discord.ext import commands

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Exceptions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Unknown Error Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class UnknownError(commands.CommandError):
    pass

class AppUnknownError(app_commands.AppCommandError):
    pass

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Operation Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BadOperation(commands.CommandError):
    def __init__(
        self,
        title    : str,
        subtitle : str | None = "An exception occured while running this command.",
    ) -> None:
        self.title    : str        = title
        self.subtitle : str | None = subtitle
        super().__init__()

class AppBadOperation(app_commands.AppCommandError):
    def __init__(
        self,
        title    : str,
        subtitle : str | None = "An exception occured while running this command.",
    ) -> None:
        self.title    : str        = title
        self.subtitle : str | None = subtitle
        super().__init__()

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BadArgument(commands.CommandError):
    def __init__(self, subtitle : dict[str, str]) -> None:
        self.subtitle : dict[str, str] = subtitle
        msg = ", ".join(f"{k}: {v}" for k, v in subtitle.items())
        super().__init__(msg)

class AppBadArgument(app_commands.AppCommandError):
    def __init__(self, subtitle : dict[str, str]) -> None:
        self.subtitle : dict[str, str] = subtitle
        msg = ", ".join(f"{k}: {v}" for k, v in subtitle.items())
        super().__init__(msg)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Command Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BadPermissionsCommand(commands.CommandError):
    pass

class AppBadPermissionsCommand(app_commands.AppCommandError):
    pass

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Permissions Argument Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BadPermissionsArgument(commands.CommandError):
    def __init__(self, *args : str) -> None:
        self.arguments : tuple[str, ...] = args
        super().__init__(f"Bad argument permissions for: {', '.join(args)}")

class AppBadPermissionsArgument(app_commands.AppCommandError):
    def __init__(self, *args : str) -> None:
        self.arguments : tuple[str, ...] = args
        super().__init__(f"Bad argument permissions for: {', '.join(args)}")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment Channel Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BadEnvironmentChannel(commands.CommandError):
    pass

class AppBadEnvironmentChannel(app_commands.AppCommandError):
    pass

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bad Environment DMs Exception
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BadEnvironmentDMs(commands.CommandError):
    pass

class AppBadEnvironmentDMs(app_commands.AppCommandError):
    pass
