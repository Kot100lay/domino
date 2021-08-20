import discord
# from discord import message
from discord.ext import commands
from discord.ext.commands import Cog
# import asyncio
import os
from datetime import datetime
# from main import prefix_
from kotjson import responses
  

class Utilities(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    '''
    @Cog.listener
    async def on_ready(self):
        print("Utilities ready")
    '''
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"{self.bot.latency}s")

    @commands.command()
    async def prefix(self, ctx):
        await ctx.send(self.bot.PREFIX)

    # ADMIN
    @commands.command()
    @commands.is_owner()
    async def extreload(self, ctx):
        loaded_extensions = 0
        extensions = 0

        for _ in os.listdir("./utils/"):
            if _.endswith(".py"):
                try:
                    self.bot.reload_extension(f"utils.{os.path.splitext(_)[0]}")
                    loaded_extensions += 1
                except Exception:
                    pass
                finally:
                    extensions += 1

        await ctx.send(f"{loaded_extensions}/{extensions} Extensions reloaded")

    # send a file from working directory in the chat
    @commands.command()
    @commands.is_owner()
    async def gib(ctx, filename):
        try:
            await ctx.send(file=discord.File(filename))
        except Exception:
            await ctx.send(responses.common_error)

    # kill the bot
    @commands.command()
    @commands.is_owner()
    async def kys(self, ctx):
        try:
            msg = responses.death
            await ctx.send(msg)
            await self.bot.close()

        except Exception:
            print("Tried to send {} but an error occured".format(msg))
        finally:
            print("Bot terminated [{}]".format(datetime.now()))

    @commands.command()
    async def purge(self, ctx: commands.context, amount: int):
        await ctx.channel.purge(limit=amount + 1)
            
    @commands.command()
    @commands.is_owner()
    async def save(self, ctx, path=''):
        for attachment in ctx.message.attachments:
            try:
                if path and path[-1] != '/': path += '/'
                await attachment.save(path + attachment.filename)
                await ctx.send(responses.file_saved.format(attachment.filename))
            except Exception as e:
                await ctx.send(responses.common_error + f"({e})")


def setup(bot):
    bot.add_cog(Utilities(bot))
