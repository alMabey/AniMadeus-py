import discord
import config
import mysql.connector
import subprocess


# Class for the bot client.
class AniMadeus(discord.Client):

    # Constructor for the AniMadeus class.
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.guild_id = 221309541088886784

        self.command_prefix = '!'

        self.message_ids = {
            'role_assign_message': 751166772542963824,
        }

        self.channel_ids = {
            'bot-commands': 222363798391095296,
            'web-development': 335158754616016906
        }

        self.role_ids = {
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

        self.emoji_to_role_mappings = {
            '1️⃣': self.role_ids['general'],
            '2️⃣': self.role_ids['art'],
            '🎵': self.role_ids['amq'],
            '↖️': self.role_ids['non-warwick'],
            '🎙️': self.role_ids['vc'],
            '🎓': self.role_ids['graduate'],
            '🎰': self.role_ids['gacha_addict'],
        }

    # Method executed when the bot has started up.
    async def on_ready(self):
        await self.change_presence(activity=config.status_activity)

    # Method executed when a reaction is added to a message.
    # This is used for the role assign system on the server.
    async def on_raw_reaction_add(self, payload):
        if payload.message_id != self.message_ids['role_assign_message']:
            return

        try:
            # If we start using custom emoji this will need editing
            role_id = self.emoji_to_role_mappings[str(payload.emoji)]
        except KeyError:
            return

        role = self.get_guild(self.guild_id).get_role(role_id)
        if role is None:
            return

        try:
            await payload.member.add_roles(role)
        except discord.HTTPException:
            pass

    # Method executed when a reaction is removed from a message.
    # This is used for the role assign system on the server.
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id != self.message_ids['role_assign_message']:
            return

        try:
            # If we start using custom emoji this will need editing
            role_id = self.emoji_to_role_mappings[str(payload.emoji)]
        except KeyError:
            return

        role = self.get_guild(self.guild_id).get_role(role_id)
        if role is None:
            return

        member = self.get_guild(self.guild_id).get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.remove_roles(role)
        except discord.HTTPException:
            pass

    # Method executed when a message is sent in the server.
    # This is used for the various commands.
    async def on_message(self, message):
        if message.content[0] == self.command_prefix:
            message_components = message.content[1:].split()
            # Commands for bot-commands
            if message.channel.id == self.channel_ids['bot-commands']:
                if message_components[0] == 'member':
                    # Command to add the "member" role to a user. Requires that they have linked their website account
                    # to their discord.
                    return await self.member_command(message, message_components)
                elif message_components[0] == 'events':
                    # Command to return upcoming society events using the website's API.
                    return await message.channel.send('{0} - This command is not currently implemented.'.format(
                        message.author.mention))
                elif message_components[0] == 'library':
                    # Command to search the society library using the website's API.
                    return await message.channel.send('{0} - This command is not currently implemented.'.format(
                        message.author.mention))
                else:
                    pass
            # Commands for web-development
            elif message.channel.id == self.channel_ids['web-development']:
                # Only members with the Exec role should be able to run these commands. As the command must also be
                # sent in the #web-development channel, this is limited to The Webmaster, The President and any exec
                # with the Admin role.
                exec_role = self.get_guild(self.guild_id).get_role(self.role_ids['exec'])
                if exec_role in message.author.roles:
                    if message_components[0] == 'website_create_users':
                        # Command to run the createusers command on the website.
                        return await self.website_create_users_command(message, message_components)
                    else:
                        pass
                else:
                    return await message.channel.send('{0} - Only exec can use these commands.'.format(
                        message.author.mention))
            # Commands for all channels
            else:
                # Command to prune a certain amount of messages from the channel.
                # Only members with the Exec role should be able to run this comand.
                if message_components[0] == 'prune':
                    exec_role = self.get_guild(self.guild_id).get_role(self.role_ids['exec'])
                    if exec_role in message.author.roles:
                        try:
                            prune_count = int(message_components[1])
                        except (ValueError, IndexError):
                            return await message.channel.send('{0} - You are using this command incorrectly. The correct usage is `!prune <amount>`.'.format(
                                message.author.mention))
                        if prune_count > 200:
                            return await message.channel.send('{0} - You can only prune up to 200 messages at once.'.format(
                                message.author.mention))
                        async for delete_message in message.channel.history(limit=prune_count):
                            await message.delete()
                        return await message.channel.send('{0} - Pruned {1} messages.'.format(
                            message.author.mention, prune_count))
                    else:
                        return await message.channel.send('{0} - Only exec can use these commands.'.format(
                            message.author.mention))
                

    # Method for handling the !member command
    async def member_command(self, message, command_components):
        if len(command_components) != 2:
            return await message.channel.send(
                '{0} - You are using this command incorrectly. The correct usage is `!member <uni_id>`.'.format(
                    message.author.mention))

        if len(command_components[1]) != 7:
            return await message.channel.send('{0} - Your university id should be 7 digits long.'.format(
                message.author.mention))

        try:
            member_id = int(command_components[1])
        except ValueError:
            return await message.channel.send('{0} - Your university id should be a 7 digit integer.'.format(
                message.author.mention))

        # As the bot runs on the same machine as the website, we can connect to the MySQL server that the site DB runs
        # on to get the discord tag that matches the specified University ID. This is prefereable to using the site API
        # as Uni ID to discord tag mappings may be considered sensitive by some, so having them on a public API is
        # a bad idea.
        try:
            conn = mysql.connector.connect(
                host=config.db_host,
                port=config.db_port,
                database=config.db_name,
                user=config.db_user,
                password=config.db_password)
        except mysql.connector.Error:
            await message.channel.send(
                '{0} - An error occurred when running this command, please wait for the webmaster to fix it.'.format(
                    message.author.mention))
            webmaster = message.guild.get_role(self.role_ids['webmaster'])
            web_development_channel = self.get_guild(self.guild_id).get_channel(self.channel_ids['web-development'])
            return await web_development_channel.send(
                '{0} - There was an SQL connection error when executing the member command.'.format(webmaster.mention))

        cursor = conn.cursor()

        query = 'SELECT discord_tag FROM members_member' \
            ' INNER JOIN auth_user ON auth_user.id = members_member.user_id' \
            ' WHERE auth_user.username = %s;'

        cursor.execute(query, (member_id,))

        tag_matched = False
        result_found = False
        for (discord_tag,) in cursor:
            result_found = True
            tag_matched = discord_tag == '{0}#{1}'.format(message.author.name, message.author.discriminator)

        conn.close()

        if tag_matched:
            member_role = self.get_guild(self.guild_id).get_role(self.role_ids['member'])
            await message.author.add_roles(member_role)
            return await message.channel.send('{0} - Member role added.'.format(message.author.mention))
        elif result_found:
            return await message.channel.send('{0} - The discord tag for this user does not match yours.'.format(
                message.author.mention))
        else:
            return await message.channel.send('{0} - No member with this ID was found.'.format(message.author.mention))

    # Method for handling the !website_create_users command
    async def website_create_users_command(self, message, command_components):
        if len(command_components) != 1:
            return await message.channel.send(
                '{0} - You are using this command incorrectly. The correct usage is `!website_create_users`.'.format(
                    message.author.mention))

        # The command needs to be run from the TengenToppaAniMango venv, so we use the subprocess module to execute it.
        process = subprocess.Popen(config.website_create_users_command.split(), stdout=subprocess.PIPE)
        # The command will either print the number of new members or the error that occurred when trying to make the
        # accounts.
        output, error = process.communicate()
        return await message.channel.send('{0} - Command output: `{1}`.'.format(
            message.author.mention, output.decode('utf-8').strip('\n')))


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True

    client = AniMadeus(intents=intents)
    client.run(config.bot_token)
