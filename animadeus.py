import discord
from discord.ext import commands
import config
import mysql.connector
import subprocess


# Global Data
GUILD_ID = 221309541088886784

MESSAGE_IDS = {
    'role_assign_message': 751166772542963824,
}

CHANNEL_IDS = {
    'bot-commands': 222363798391095296,
    'web-development': 335158754616016906,
    'newcomers': 753668259974217870,
    'rules': 385333508463263746,
    'role-assign': 546843849620979723,
    'welcome-and-links': 326044428621840386
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
    'exec': 221311015432749056
}

EMOJI_TO_ROLE_MAPPINGS = {
    '1️⃣': ROLE_IDS['general'],
    '2️⃣': ROLE_IDS['art'],
    '🎵': ROLE_IDS['amq'],
    '↖️': ROLE_IDS['non-warwick'],
    '🎙️': ROLE_IDS['vc'],
    '🎓': ROLE_IDS['graduate'],
    '🎰': ROLE_IDS['gacha_addict']
}

# Intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True

# Bot instance
bot = commands.Bot(command_prefix='!', description='The Warwick Anime & Manga Society Discor Bot.', intents=intents)


# Startup event.
#
# Currently only sets the status.
@bot.event
async def on_ready():
    await bot.change_presence(activity=config.status_activity)


# Bot-commands check.
#
# Checks if a command was run in the bot-commands channel.
def bot_commands_channel_check(ctx):
    return ctx.message.channel.id == CHANNEL_IDS['bot-commands']


# Web-development check.
#
# Checks if a command was run in the web-development channel.
def web_development_channel_check(ctx):
    return ctx.message.channel.id == CHANNEL_IDS['web-development']


# Event listener for member joins.
#
# Used to welcome new users.
@bot.listen()
async def on_member_join(member):
    guild = bot.get_guild(GUILD_ID)
    newcomers_channel = guild.get_channel(CHANNEL_IDS['newcomers'])
    welcome_channel = guild.get_channel(CHANNEL_IDS['welcome-and-links'])
    rules_channel = guild.get_channel(CHANNEL_IDS['rules'])
    role_channel = guild.get_channel(CHANNEL_IDS['role-assign'])
    welcome_string = ('Welcome to the Warwick Anime and Manga Society Discord serever, {0}!'
                      ' Please see {1} and {2} for information about the society and this server.'
                      'To gain access to the rest of the server please react to the message in {3}!')
    await newcomers_channel.send(
        welcome_string.format(member.mention, welcome_channel.mention, rules_channel.mention, role_channel.mention))


# Event listener for reaction adds.
#
# Used for the role assign system.
@bot.listen()
async def on_raw_reaction_add(payload):
    if payload.message_id != MESSAGE_IDS['role_assign_message']:
        return

    try:
        # If we start using custom emoji this will need editing
        role_id = EMOJI_TO_ROLE_MAPPINGS[str(payload.emoji)]
    except KeyError:
        return

    role = bot.get_guild(GUILD_ID).get_role(role_id)
    if role is None:
        return

    try:
        await payload.member.add_roles(role)
    except discord.HTTPException:
        pass


# Event listener for reaction removals.
#
# Used for the role assign system.
@bot.listen()
async def on_raw_reaction_remove(payload):
    if payload.message_id != MESSAGE_IDS['role_assign_message']:
        return

    try:
        # If we start using custom emoji this will need editing
        role_id = EMOJI_TO_ROLE_MAPPINGS[str(payload.emoji)]
    except KeyError:
        return

    role = bot.get_guild(GUILD_ID).get_role(role_id)
    if role is None:
        return

    member = bot.get_guild(GUILD_ID).get_member(payload.user_id)
    if member is None:
        return

    try:
        await member.remove_roles(role)
    except discord.HTTPException:
        pass


# Member command.
#
# Used to assign users the Member role.
#
# The member role is assigned to users that have linked their website (animesoc.co.uk) account with their discord.
# The current website API is barebones and lacks any form of authentication. Discord tag to member's website accounts
# could be considered sensitive by some. So to avoid needing to implement authentication on the API the bot connects
# to the MYSQL server that contains the site's database to find the discord tag.
#
# For this command to work the bot must be running on the same machine as the website's database.
@bot.command(pass_context=True)
@commands.check(bot_commands_channel_check)
async def member(ctx, member_id: int):
    if len(str(member_id)) != 7:
        return await ctx.message.channel.send('{0} - Your university id should be 7 digits long.'.format(
            ctx.message.author.mention))

    try:
        conn = mysql.connector.connect(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_password)
    except mysql.connector.Error:
        await ctx.message.channel.send(
            '{0} - An error occurred when running this command, please wait for the webmaster to fix it.'.format(
                ctx.message.author.mention))
        webmaster = ctx.message.guild.get_role(ROLE_IDS['webmaster'])
        web_development_channel = bot.get_guild(GUILD_ID).get_channel(CHANNEL_IDS['web-development'])
        return await web_development_channel.send(
            '{0} - There was an SQL connection error when executing the member command.'.format(webmaster.mention))

    cursor = conn.cursor()

    query = ('SELECT discord_tag FROM members_member'
             ' INNER JOIN auth_user ON auth_user.id = members_member.user_id'
             ' WHERE auth_user.username = %s;')

    cursor.execute(query, (member_id,))

    tag_matched = False
    result_found = False
    for (discord_tag,) in cursor:
        result_found = True
        tag_matched = discord_tag == '{0}#{1}'.format(ctx.message.author.name, ctx.message.author.discriminator)

    conn.close()

    if tag_matched:
        member_role = bot.get_guild(GUILD_ID).get_role(ROLE_IDS['member'])
        await ctx.message.author.add_roles(member_role)
        return await ctx.message.channel.send('{0} - Member role added.'.format(ctx.message.author.mention))
    elif result_found:
        return await ctx.message.channel.send('{0} - The discord tag for this user does not match yours.'.format(
            ctx.message.author.mention))
    else:
        return await ctx.message.channel.send('{0} - No member with this ID was found.'.format(
            ctx.message.author.mention))


# Member command error handler.
@member.error
async def on_member_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        return await ctx.message.channel.send(
            '{0} - You are using this command incorrectly. The correct usage is `!member <uni_id>`.'.format(
                ctx.message.author.mention))
    elif isinstance(error, commands.errors.BadArgument):
        return await ctx.message.channel.send('{0} - Your university id should be a 7 digit integer.'.format(
            ctx.message.author.mention))
    elif isinstance(error, commands.errors.CheckFailure):
        pass

# Create_website_user command.
#
# Run the command to create users on the website.
#
# This command uses the subprocesses module to run the command which creates users on the website and sends out the
# welcome emails.
#
# Only the webmaster can use this command and it must be in the web-development channel.
#
# For this command to work the bot must be running on the same machine as the website.
@bot.command(pass_context=True)
@commands.has_role(ROLE_IDS['webmaster'])
@commands.check(web_development_channel_check)
async def website_create_users(ctx):
    process = subprocess.Popen(config.website_create_users_command.split(), stdout=subprocess.PIPE)
    # The command will either print the number of new members or the error that occurred when trying to make the
    # accounts.
    output, _ = process.communicate()
    return await ctx.message.channel.send('{0} - Command output: `{1}`.'.format(
        ctx.message.author.mention, output.decode('utf-8').strip('\n')))


# Create_website_user command error handler.
@website_create_users.error
async def on_website_create_users_error(ctx, error):
    if isinstance(error, commands.errors.MissingRole):
        return await ctx.message.channel.send(
            '{0} - Only the webmaster can use this command.'.format(
                ctx.message.author.mention))
    elif isinstance(error, commands.errors.CheckFailure):
        return await ctx.message.channel.send('{0} - You must use this command in the web-development channel.'.format(
            ctx.message.author.mention))


# Prune command.
#
# Prunes up to 100 messages.
#
# Only exec can use this command.
@bot.command()
@commands.has_role(ROLE_IDS['exec'])
async def prune(ctx, prune_amount: int):
    if prune_amount > 100:
        return await ctx.message.channel.send(
            '{0} - You can only prune up to 100 messages at once.'.format(
                ctx.message.author.mention))
    elif prune_amount < 0:
        return await ctx.message.channel.send(
            '{0} - The amount of messages to prune must be a postive integer.'.format(
                ctx.message.author.mention))

    deleted = await ctx.message.channel.purge(limit=prune_amount)
    return await ctx.message.channel.send('{0} - Pruned {1} messages.'.format(
        ctx.message.author.mention, len(deleted)), delete_after=5)


# Prune command error handler.
@prune.error
async def on_prune_error(ctx, error):
    if isinstance(error, commands.errors.MissingRole):
        return await ctx.message.channel.send(
            '{0} - Only the exec can use this command.'.format(
                ctx.message.author.mention))
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        return await ctx.message.channel.send(
            '{0} - You are using this command incorrectly. The correct usage is `!prune <amount>`.'.format(
                ctx.message.author.mention))
    elif isinstance(error, commands.errors.BadArgument):
        return await ctx.message.channel.send(
            '{0} - The amount of messages to prune must be a postive integer.'.format(
                ctx.message.author.mention))


# Events command.
#
# Returns a formatted list of upcoming events.
#
# This command was implemented in the old Animadeus bot, however no one ever really used it so this is a very low
# priority feature.
@bot.command(pass_context=True)
async def events(ctx):
    message_string = ('{0} - This command is not currently implemented'
                      ' ~~and probably wont be for a very long time~~.')
    return await ctx.message.channel.send(message_string.format(
        ctx.message.author.mention))


# Library command.
#
# Returns a formatted list of library titles that match a search string.
#
# This command was implemented in the old Animadeus bot, however no one ever really used it so this is a very low
# priority feature.
@bot.command(pass_context=True)
async def library(ctx):
    message_string = ('{0} - This command is not currently implemented'
                      ' ~~and probably wont be for a very long time~~.')
    return await ctx.message.channel.send(message_string.format(
        ctx.message.author.mention))


if __name__ == '__main__':
    bot.run(config.bot_token)
