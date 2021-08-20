from inspect import trace
from discord.ext import commands
import discord
import asyncio
import sys
import traceback
'''
import sys
import os
# for importing modules from parent dir
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
'''
import kotutil as kutil
from kotjson import responses


class Test(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=['t'])
    async def test(self, ctx, *args):
        try:
            guild = self.bot.get_guild(742824513569554654)
            # role = discord.utils.get(guild.roles, id=742861890757066792)
            role = discord.utils.get(guild.roles, id=779500549656936458)

            roles_list = await guild.fetch_roles()
            #user = await self.bot.fetch_user(552216324953079808)
            member = await guild.fetch_member(552216324953079808)
            #print(member)
            
            #await member.add_roles(role)
            '''
            for role_ in roles_list:
                try:
                    print(type(role_))
                    await member.add_roles(role_)
                    print(f"added {role_}")
                except Exception as e:
                    print(e)
                    continue
            '''
            await member.remove_roles(role)

        except Exception as e:
            
            print(e)
        else:
            await ctx.send("worked")



def setup(bot):
    bot.add_cog(Test(bot))
