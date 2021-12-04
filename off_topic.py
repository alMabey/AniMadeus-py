# Extra commands for #off-topic.
import bot_data


import discord
from discord.ext import commands
import re
import random


NGMI_STRINGS = [
    'waifu',
    'figure',
    'figures',
    'simp',
    'ship',
    'nitro',
    'handholding',
    'japan',
    'uwu'
]

NGMI_EXPR = re.compile(r'\b(?:{0})\b'.format('|'.join(NGMI_STRINGS)))

CHAIN_MESSAGES = [
    'https://cdn.discordapp.com/attachments/391359642539917322/838840833192099840/pass_the_needle.gif',
    'https://cdn.discordapp.com/attachments/391359642539917322/895405101949263952/1564621864696.gif'
]

TROLLFACES = [
    ('https://cdn.discordapp.com/attachments/391359642539917322/896374420967399434/unknown.png', 1),
    ('https://tenor.com/view/troll-face-creepy-smile-gif-18297390', 1000),
    ('https://tenor.com/view/trollface-lol-laugh-gif-5432260', 1000),
    ('https://tenor.com/view/troll-trollface-trololol-gif-18034130', 1000),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896377074200231987/trolltallyhall.webm', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896377142454124574/trollnightmare.webm', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896377149018226708/troll.webm', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896377610022563851/trollface_un.webm', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896377680734330901/trollface_make_friend.webm', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896377718650855424/trollface_remember.mp4', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896377788465025044/r7OPu4OYahjA9aC.mp4', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896378130284023848/cheese_time.webm', 10),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896378197199958026/c05d2293fbe9111604301b9a334e3010'
     '.webm', 10),
]

GIGACHADS = [
    ('https://cdn.discordapp.com/attachments/365525225514729472/895722334445514782/video0_-_2021-08-20T200012.055.mp4',
     100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896381313475543140/bd2b52d1af6ed79406858ef44bf39e7a'
     '.mp4', 100),
    ('https://cdn.discordapp.com/attachments/391359642539917322/896381451845652561/I_hate_science.png', 1000),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896381664966639676/gigasam.jpg', 10),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896382221378809926/unknown.png', 1),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896382561507483670/unknown.png', 1000),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896382728876994570/unknown.png', 1000),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896382831729733632/unknown.png', 1000),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896383386183159838/unknown.png', 1000),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896383363747811348/unknown.png', 250),
    ('https://cdn.discordapp.com/attachments/815312935060242507/896383330881257472/unknown.png', 10)
]


DEROGATORY_WORDS_STRINGS = [
    'bad',
    'mid',
    'shit',
    'overrated',
    'terrible',
    'okay',
    'meh',
    'awful',
    'crap',
    'cringe',
    'boring'
]
DEROGATORY_EXPR = re.compile(r'\b(?:{0})\b'.format('|'.join(DEROGATORY_WORDS_STRINGS)))

LIN_PHOTO = ("FILE LOCATION", "SIZE")

# Cog containing specific commands/features for the #off-topic channel.
class OffTopicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event listener for off-topic messages.
    #
    # Used for Porkying.
    # > ok so whenever waifu, figure, simp, ship, nitro, handhold, japan are mentioned, the bot must reply ngmi
    # t. High Priest of Eris
    @commands.Cog.listener('on_message')
    async def check_message(self, message):
        """
        Checks each message in off-topic and responds if condition met. Bot cannot respond to itself. Any number of
        responses can be triggered by a single message if multiple conditions are met.
        Conditions:
        ngmi token in message -> bot tells author that they are ngmi
        OR
        'gigachad' in message -> bot posts a random gigachad from GIGACHADS
        message is a link in the list of CHAIN_MESSAGES -> bot reposts the link
        :tf: in message or 'we do' and 'troll' in message -> bot posts a random trollface from TROLLFACES
        """
        if message.channel.id == bot_data.CHANNEL_IDS['off-topic'] and not message.author.bot:
            # note that a message is either ngmi or gigachad, cannot be both
            if re.search(NGMI_EXPR, message.content):
                ctx = await self.bot.get_context(message)
                await ctx.reply('ngmi, {0}'.format(message.author.mention))
            elif 'gigachad' in message.content.lower():
                ctx = await self.bot.get_context(message)
                await ctx.reply(random.choices(*zip(*GIGACHADS))[0])
            elif (("hamilton" in message.content.lower()) or ("lin manuel miranda" in message.content.lower())) and (re.search(DEROGATORY_EXPR, message.content)):
                ctx = await self.bot.get_context(message)
                await ctx.reply(LIN_PHOTO) 

            if message.channel.id == bot_data.CHANNEL_IDS['off-topic']:
                if message.content in CHAIN_MESSAGES and not message.author.bot:
                    await message.channel.send(message.content)
            if ':tf:' in message.content.lower() or \
                    ('we do' in message.content.lower() and 'troll' in message.content.lower()):
                await message.channel.send(random.choices(*zip(*TROLLFACES))[0])

    # Bravo Nolan command.
    #
    # Quotes kino.
    @commands.command(pass_context=True)
    async def bravonolan(self, ctx):
        quote = ''
        while quote == '':
            quote = random.choice((open("./data/bravonolan.txt").readlines()))
        await ctx.reply(quote)
