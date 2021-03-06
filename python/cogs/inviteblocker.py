"""This is a cog for a discord.py bot.
It will auto delete messages that contain discord invite links

Commands:
    allow           Specify a user. User is then allowed to post 1
                    discord.gg invite link

Load the cog by calling client.load_extension with the name of this python file
as an argument (without the file-type extension)
    example:    bot.load_extension('inviteblocker')
or by calling it with the path and the name of this python file
    example:    bot.load_extension('cogs.inviteblocker')

Only users belonging to a role that is specified under the module's name
in the permissions.json file can use the commands.
"""

from discord.ext import commands
from discord import Member
from os import path
import json
import re


class InviteBlocker():
    def __init__(self, client):
        self.client = client
        self.allowed = []
        with open(path.join(path.dirname(__file__), 'permissions.json')) as f:
            self.permitted_roles = json.load(f)[__name__.split('.')[-1]]


    async def __local_check(self, ctx):
        # if await ctx.bot.is_owner(ctx.author):
        #     return True
        try:
            user_roles = [role.id for role in ctx.message.author.roles]
        except AttributeError:
            return False
        return any(role in self.permitted_roles for role in user_roles)

    async def check_message(self, msg):
        if msg.author.bot:
            # Dont check messages of bots
            return
        if msg.channel.guild is None:
            # Dont check Direct Messages
            return False
        author_roles = [role.id for role in msg.author.roles]
        if any(role in self.permitted_roles for role in author_roles):
            # Don't check messages by users with allowed roles
            return False
        if len(re.findall(r'(?i)(discord\.(gg|io|me)\/\S+)', msg.content)):
            if msg.author.id in self.allowed:
                self.allowed.remove(msg.author.id)
            else:
                await msg.channel.send(
                    f'Sorry {msg.author.mention}. ' +
                    'Posting Links to other servers is not allowed.\n' +
                    'You can ask permission from an admin or moderator!'
                )
                await msg.delete()

    # ----------------------------------------------
    # Event listeners
    # ----------------------------------------------
    async def on_message(self, msg):
        await self.check_message(msg)

    async def on_message_edit(self, before, after):
        await self.check_message(after)

    # ----------------------------------------------
    # Method to allow 1 discord.gg link
    # ----------------------------------------------
    @commands.command(
        name='allow',
        brief='Allow a single discord.gg link.',
        description='Allow a single discord.gg link.',
        hidden=True,
    )
    @commands.guild_only()
    async def allow(self, ctx, member: Member):
        await ctx.send(f'Hey {member.mention}, you can post 1 discord.gg link!')
        self.allowed.append(member.id)


def setup(client):
    client.add_cog(InviteBlocker(client))
