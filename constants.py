from enum import Enum

from discord import Color

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Constants
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Enums
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class DisplayNameFont(Enum):
    bangers       = 1  # Unimplemented
    bio_rhyme     = 2  # Unimplemented
    cherry_bomb   = 3
    chicle        = 4
    compagnon     = 5  # Unimplemented
    museo_moderno = 6
    neo_castel    = 7
    pixelify      = 8
    ribes         = 9  # Unimplemented
    sinistre      = 10
    default       = 11
    zilla_slab    = 12

class DisplayNameEffect(Enum):
    solid    = 1
    gradient = 2
    neon     = 3
    toon     = 4
    pop      = 5
    glow     = 6  # Unimplemented


# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Colors
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


COLOR_BLURPLE = Color(0x5765F2)
COLOR_BLUE    = Color(0x87acdf)
COLOR_GREEN   = Color(0x3BA562)
COLOR_YELLOW  = Color(0xF1B133)
COLOR_ORANGE  = Color(0xEE773E)
COLOR_RED     = Color(0xEB3D48)
COLOR_BLACK   = Color(0x000000)
COLOR_GREY    = Color(0xABABAB)
COLOR_WHITE   = Color(0xFFFFFF)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# User IDs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

BOT_OWNER_ID = 1311394031640776716

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# User Mentions
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

BOT_OWNER_MENTION = "<@1311394031640776716>"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Server IDs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

SUPPORT_GUILD_ID = 1537571856964386971

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Channel IDs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

BOT_ERRORS_LOG_CHANNEL_ID = 1537572340228038740

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Emoji Strings
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

EMPLOYEE_EMOJI = "<:employee:1526002139388842075>"

DEVELOPER_EMOJI = "<:developer:1528046387143376971>"

BIG_BOT_EMOJI = "<:bot1:1526024929328365611><:bot2:1526024984739446914>"
BOT_EMOJI = "<:bot:1526025119397318828>"

PARTNER_EMOJI = "<:partner:1526020738019102780>"

OWNER_EMOJI = "<:owner:1526002022384664606>"

MODERATOR_EMOJI                   = "<:moderator:1525517002511220846>"
ADMINISTRATOR_EMOJI               = "<:administrator:1525516899704901787>"
MODERATOR_AND_ADMINISTRATOR_EMOJI = "<:moderator_and_administrator:1525516827982041281>"
DIRECTOR_EMOJI                    = "<:director:1525516765004562452>"

BOOSTER_EMOJI = "<:booster:1526003525656514713>"

PARTNERED_SERVER_EMOJI      = "<:partnered_server:1526007129440260278>"
VERIFIED_SERVER_EMOJI       = "<:verified_server:1526007081973448787>"
BOOSTED_GLOBAL_SERVER_EMOJI = "<:boosted_global_server:1526007178035724360>"
BOOSTED_SERVER_EMOJI        = "<:boosted_server:1526007228983939143>"
GLOBAL_SERVER_EMOJI         = "<:global_server:1526007284977762436>"
SERVER_EMOJI                = "<:server:1526006935709548646>"

CATEGORY_EMOJI            = "<:category:1529676328230715534>"
RULES_EMOJI               = "<:rules:1526236777084620811>"
LOCKED_ANNOUNCEMENT_EMOJI = "<:locked_announcement:1526234327975985322>"
ANNOUNCEMENT_EMOJI        = "<:announcement:1526234373916196965>"
ACTIVE_LOCKED_STAGE_EMOJI = "<:locked_active_stage:1526233549794054216>"
ACTIVE_STAGE_EMOJI        = "<:active_stage:1526233499244171276>"
LOCKED_STAGE_EMOJI        = "<:locked_stage:1526233453597687968>"
STAGE_EMOJI               = "<:stage:1526233400686415932>"
ACTIVE_LOCKED_VOICE_EMOJI = "<:active_locked_voice:1526231750534238479>"
ACTIVE_VOICE_EMOJI        = "<:active_voice:1526231806548906004>"
LOCKED_VOICE_EMOJI        = "<:locked_voice:1526231591783895070>"
VOICE_EMOJI               = "<:voice:1526231692132614154>"
LOCKED_FORUM_EMOJI        = "<:locked_forum:1514059599530037329>"
FORUM_EMOJI               = "<:forum:1526229245943218368>"
LOCKED_MEDIA_EMOJI        = "<:locked_media:1526236949059473439>"
MEDIA_EMOJI               = "<:media:1526236896601178284>"
LOCKED_TEXT_EMOJI         = "<:locked_text:1526229560675270888>"
TEXT_EMOJI                = "<:text:1526229652178473013>"
THREAD_EMOJI              = "<:thread:1526251310704230632>"

ACCEPTED_EMOJI   = "<:accepted:1522673221781164275>"
CONTESTED_EMOJI  = "<:contested:1514059240967245996>"
DENIED_EMOJI     = "<:denied:1514059386711048264>"
STANDSTILL_EMOJI = "<:standstill:1514059459721429042>"

ARROW_EMOJI         = "<:arrow:1530347836087074948>"
MEMBER_EMOJI        = "<:member:1529628347460489266>"
PENCIL_EMOJI        = "<:pencil:1529627235231727697>"
PARTNERSHIP_EMOJI   = "<:partnership:1529625058690076722>"
QUERY_EMOJI         = "<:query:1529292799164289196>"
SEARCH_EMOJI        = "<:search:1528860997396201564>"
HORIZONTAL_SETTINGS = "<:horizontal_settings:1528938420490211459>"
MODERATION_EMOJI    = "<:moderation:1528939256557342751>"
COMMAND_EMOJI       = "<:command:1528781249718517951>"
EMOJI_EMOJI         = "<:emoji:1528940345763827775>"

PET_CORDEX_EMOJI = "<a:pet_cordex:1526024713078571141>"
