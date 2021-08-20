from discord.ext import commands
import discord
import kotutil as kutil
from kotjson import responses


@commands.command(aliases=["karzeł", "karzel"])
@commands.is_nsfw()
async def midget(ctx, mode='sfw'):
    try:
        async with ctx.typing():
            midget = kutil.random_midget(mode=mode)
            embed = discord.Embed(title = responses.midgetporn+"(?)", type='rich', colour=0xffc0cb)
            embed.set_image(url=midget)
    except:
        await ctx.send(responses.common_errors)
    else:
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(midget)

