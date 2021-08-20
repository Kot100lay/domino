from discord.ext import commands
# import os
import datetime  # logs, mainly
import sys  # sys.platform for setting the prefix
# cogs
from glob import glob
import discord
# import kotutil as kutil
# from kotjson import responses
import kotjson
responses = kotjson.responses

if sys.platform == "win32":
    PREFIX = ">"
    COGS = [path.split("\\")[-1][:-3] for path in glob("./utils/*.py")]
else:
    PREFIX = "]"
    COGS = [path.split("/")[-1][:-3] for path in glob("./utils/*.py")]
    
OWNER_IDS = [552216324953079808]

LOG_CHANNEL = 876887262422532107
CARETAKER_IDS = [552216324953079808]  # = owner_ids atm


async def bot_log(bot, message: str, importance=1):
    '''
    importance -> [0 - only printing to the console,
    1 - console and LOG_CHANNEL,
    2(max) - CARETAKER_IDS + all above]'''
    message = f"[{datetime.datetime.now()}]\n{message}"
    print(message)

    try:  # internet connection check
        if importance > 1:
            for id in CARETAKER_IDS:
                user = await bot.fetch_user(id)
                await user.send(message)
        if importance > 0:
            log_channel = bot.get_channel(LOG_CHANNEL)
            await log_channel.send(message)
    except Exception as e:
        print(e)


class Bot(commands.Bot):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.TOKEN = "NzE3ODM5NzYwMjAyMjY4Nzk3.XtgLFw.AmcYbdbNOVdpnRrT_A00XHr1Y-U"
        # TODO debugging channel and a method (somewhere) for both logging and printing out messages

        super().__init__(command_prefix=commands.when_mentioned_or(PREFIX), owner_ids=OWNER_IDS, activity=discord.Game("Poker"))

    def setup(self):
        for cog in COGS:
            try:
                self.load_extension(f"utils.{cog}")
            except Exception as e:
                print(e)

    def run(self, version):
        self.VERSION = version

        print("loading cogs...")
        self.setup()

        print("starting the bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        await bot_log(self, "connected", importance=2)

    async def on_disconnect(self):
        await bot_log(self, "disconnected", importance=0)

    async def on_ready(self):
        if not self.ready:
            await bot_log(self, responses.ready, importance=1)
            self.ready = True

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send(responses.command_not_found)
            return None

        raise error
    
    @commands.Cog.listener("on_message_edit")
    async def on_message_edit(self, _, after):
        await super().process_commands(after)
    

bot = Bot()

VERSION = "0.0.1"
bot.run(VERSION)
