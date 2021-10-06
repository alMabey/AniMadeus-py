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


# Cog containing specific commands/features for the #off-topic channel.
class OffTopicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event listener for ngmi messages.
    #
    # Used for Porkying.
    # > ok so whenever waifu, figure, simp, ship, nitro, handhold, japan are mentioned, the bot must reply ngmi
    # t. High Priest of Eris
    @commands.Cog.listener('on_message')
    async def ngmi_check(self, message):
        if message.channel.id == bot_data.CHANNEL_IDS['off-topic']:
            if re.search(NGMI_EXPR, message.content):
                ctx = await self.bot.get_context(message)
                await ctx.reply('ngmi, {0}'.format(message.author.mention))

    # Event listener for chain messages.
    #
    # Used for spamming.
    @commands.Cog.listener('on_message')
    async def chain_check(self, message):
        if message.channel.id == bot_data.CHANNEL_IDS['off-topic']:
            if message.content in CHAIN_MESSAGES and not message.author.bot:
                await message.channel.send(message.content)

    # Bravo Nolan command.
    #
    # Quotes kino.
    @commands.command(pass_context=True)
    async def bravonolan(self, ctx):
        quote = ''
        while quote == '':
            quote = random.choice((open("./data/bravonolan.txt").readlines()))
        await ctx.reply(quote)
