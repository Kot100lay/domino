from discord.ext import commands
import datetime
import asyncio


class Scheduler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.running = False
        
    @commands.command()
    @commands.is_owner()
    async def papieska(self, ctx):
        lolek_channel = self.bot.get_channel(742864484078715062)
        if not self.running:
            self.running = True
            while 1:
                if datetime.datetime.now().hour == 21 and datetime.datetime.now().minute == 37:
                    await lolek_channel.send("Papieska, kuhwy <:drkurwa:878030924875464796>\n @here")
                await asyncio.sleep(60)

   
def setup(bot):
    bot.add_cog(Scheduler(bot))
