# Bot data
#
# Mainly contains ids from the discord server. Leaving this out of the config file so it can be edited
# by non-webmasters.

GUILD_ID = 221309541088886784

MESSAGE_IDS = {
    'role_assign_message': 751166772542963824,
    'mcm_message': 901227550129393704  # TEMP
}

CHANNEL_IDS = {
    'bot-commands': 222363798391095296,
    'web-development': 335158754616016906,
    'newcomers': 753668259974217870,
    'rules': 385333508463263746,
    'role-assign': 546843849620979723,
    'welcome-and-links': 326044428621840386,
    'off-topic': 391359642539917322
}

ROLE_IDS = {
    'general': 546855453603135489,
    'art': 602883577293832202,
    'amq': 602883609057165363,
    'non-warwick': 729027269074485339,
    'vc': 730475391298568234,
    'graduate': 729027220139409469,
    'gacha_addict': 790246791320436796,
    'webmaster': 335157257346220033,
    'member': 472915800081170452,
    'exec': 221311015432749056,
    'mcm': 901224845067583550  # TEMP
}

EMOJI_TO_ROLE_MAPPINGS = {
    '1️⃣': ROLE_IDS['general'],
    '2️⃣': ROLE_IDS['art'],
    '🎵': ROLE_IDS['amq'],
    '↖️': ROLE_IDS['non-warwick'],
    '🎙️': ROLE_IDS['vc'],
    '🎓': ROLE_IDS['graduate'],
    '🎰': ROLE_IDS['gacha_addict'],
    '🚄': ROLE_IDS['mcm']  # TEMP
}
