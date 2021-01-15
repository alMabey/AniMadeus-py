import discord
import config
import mysql.connector
import subprocess


class AniMadeus(discord.Client):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.guild_id = 221309541088886784

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
            'misc': 602883910753583154,
            'amq': 602883609057165363,
            'non-warwick': 729027269074485339,
            'vc': 730475391298568234,
            'graduate': 729027220139409469,
            'minecraft': 758088431065759836,
            'webmaster' : 335157257346220033,
            'member': 472915800081170452,
            'exec': 221311015432749056
        }

        self.emoji_to_role_mappings = {
            '1️⃣': self.role_ids['general'],
            '2️⃣': self.role_ids['art'],
            '3️⃣': self.role_ids['misc'],
            '🎵': self.role_ids['amq'],
            '↖️': self.role_ids['non-warwick'],
            '🎙️': self.role_ids['vc'],
            '🎓': self.role_ids['graduate'],
            '⛏️': self.role_ids['minecraft'],
        }


    async def on_ready(self):
        await self.change_presence(activity=config.status_activity)

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

    async def on_message(self, message):
        if message.channel.id == self.channel_ids['bot-commands'] and message.content[0] == '!':
            message_components = message.content.split()
            if message_components[0] == '!member':
                return await self.member_command(message, message_components)
            elif message_components[0] == '!events':
                return await message.channel.send('{0} - This command is not currently implemented.'.format(message.author.mention))
            elif message_components[0] == '!library':
                return await message.channel.send('{0} - This command is not currently implemented.'.format(message.author.mention))
            else:
                return await message.channel.send('{0} - This command does not exist.'.format(message.author.mention))

        if message.channel.id == self.channel_ids['web-development'] and message.content[0] == '!':
            exec_role = self.get_guild(self.guild_id).get_role(self.role_ids['exec'])
            if exec_role in message.author.roles:
                message_components = message.content.split()
                if message_components[0] == '!website_create_users':
                    return await self.website_create_users_command(message, message_components)
                else:
                    return await message.channel.send('{0} - This command does not exist.'.format(message.author.mention))
            else:
                return await message.channel.send('{0} - Only exec can use these commands.'.format(message.author.mention))

    async def member_command(self, message, command_components):
        if len(command_components) != 2:
            return await message.channel.send('{0} - You are using this command incorrectly. The correct usage is `!member <uni_id>`.'.format(message.author.mention))

        if len(command_components[1]) != 7:
            return await message.channel.send('{0} - Your university id should be 7 digits long.'.format(message.author.mention))

        try:
            member_id = int(command_components[1])
        except ValueError:
            return await message.channel.send('{0} - Your university id should be a 7 digit integer.'.format(message.author.mention))

        try:
            conn = mysql.connector.connect(host=config.db_host, port=config.db_port, database=config.db_name, user=config.db_user, password=config.db_password)
        except mysql.connector.Error:
            await message.channel.send('{0} - An error occurred when running this command, please wait for the webmaster to fix it.'.format(message.author.mention))
            webmaster = message.guild.get_role(self.role_ids['webmaster'])
            web_development_channel = self.get_guild(self.guild_id).get_channel(self.channel_ids['web-development'])
            return await web_development_channel.send('{0} - There was an SQL connection error when executing the member command.'.format(webmaster.mention))

        cursor = conn.cursor()

        query = ('SELECT discord_tag FROM members_member INNER JOIN auth_user ON auth_user.id = members_member.user_id WHERE auth_user.username = %s')

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
            return await message.channel.send('{0} - The discord tag for this user does not match yours.'.format(message.author.mention))
        else:
            return await message.channel.send('{0} - No member with this ID was found.'.format(message.author.mention))

    async def website_create_users_command(self, message, command_components):
        if len(command_components) != 1:
            return await message.channel.send('{0} - You are using this command incorrectly. The correct usage is `!website_create_users`.'.format(message.author.mention))
        
        process = subprocess.Popen(config.website_create_users_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return await message.channel.send('{0} - Command output: `{1}`.'.format(message.author.mention, output.decode('utf-8').strip('\n')))


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.messages = True

    client = AniMadeus(intents=intents)
    client.run(config.bot_token)
