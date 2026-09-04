from typing import Self, final, override

from discord import Member

from bot import Interaction
from bot.types import GuildMessagable
from bot.ui import Checkbox, Item, Label, LayoutView, Modal, TextInput

from .actions import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Select Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class ModerationModal(Modal):
    def __init__(
        self,
        action_type : ActionType,
        target      : Member | GuildMessagable,
    ) -> None:
        target_name = target.name

        if isinstance(target, GuildMessagable) and action_type != "Purge":
            error = 'target cannot be GuildMesseagable if action_type != "Purge"'
            raise ValueError(error)

        if isinstance(target, Member) and action_type == "Purge":
            error = 'target cannot be Member if action_type == "Purge"'
            raise ValueError(error)

        title : dict[ActionType, str] = {
            "Ban Add"           : f"Banning {target_name}",
            "Ban Remove"        :  "Unbanning a Member",
            "Kick"              : f"Kick {target_name}",
            "Quarantine Add"    : f"Place {target_name} in Quarantine",
            "Quarantine Remove" : f"Remove {target_name} from Quarantine",
            "Timeout Add"       : f"Place {target_name} in Timeout",
            "Timeout Remove"    : f"Remove {target_name} from Timeout",
            "Purge"             : f"Purging {target_name}",
        }
        name : dict[ActionType, str] = {
            "Ban Add"           : "ban",
            "Ban Remove"        : "ban removal",
            "Kick"              : "kick",
            "Quarantine Add"    : "quarantine",
            "Quarantine Remove" : "quarantine removal",
            "Timeout Add"       : "timeout",
            "Timeout Remove"    : "timeout removal",
            "Purge"             : "purge",
        }

        self.name = name[action_type]

        super().__init__(title = title[action_type])

        items : list[Item[Self]] = []

        self._reason = TextInput[Self](placeholder = "Enter reason here...")
        self.reason  = Label[Self](
            text        =  "Reason",
            description = f"Reason for the {self.name}.",
            component   = self._reason,
        )

        items.append(self.reason)

        is_lengthable = action_type.endswith("Add")
        if is_lengthable:
            is_permanent     = (action_type == "Ban Add")
            length_statement = " Defaults to permanent." if is_permanent else ""

            self._length = TextInput[Self](placeholder = "Enter length here...", required = not is_permanent)
            self.length  = Label[Self](
                text        =  "Length",
                description = f"Length of the {self.name}.{length_statement}",
                component   = self._length,
            )

            items.append(self.length)

        match action_type:
            case "Ban Add":
                self._dtd = TextInput[Self](placeholder = "Enter number here...", required = False)
                self.dtd  = Label[Self](
                    text        = "Days to Delete",
                    description = "Days to delete messages of the user upon ban. Defaults to 7.",
                    component   = self._dtd,
                )

                items.append(self.dtd)
            case "Ban Remove":
                self._memberid = TextInput[Self](placeholder = "Enter ID here...")
                self.memberid  = Label[Self](
                    text        = "Member ID",
                    description = "ID of the member to unban.",
                    component   = self._memberid,
                )
            case "Purge":
                ...
            case _:
                pass

        self._dm = Checkbox[Self]()
        self.dm  = Label[Self](
            text        =  "DM",
            description = f"Whether to DM the user upon {self.name}. This can fail!",
            component   = self._dm,
        )

        items.append(self.dm)

        self.append_items(items)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        class ModerationView(LayoutView):
            ...
