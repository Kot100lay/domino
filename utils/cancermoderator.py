from discord.ext import commands
import discord
# import asyncio

import cv2
from PIL import Image
import imagehash
import os


def cancer_detect_img(source, text_or_logo="logo") -> bool:
    if text_or_logo == "logo":
        logo = cv2.imread('utils/logo.png')
    elif text_or_logo == "text":
        logo = cv2.imread('utils/text_logo.png')
    else:
        raise NameError("compared image must be either 'text' or 'logo' you idiot")

    method = cv2.TM_SQDIFF_NORMED
    image = source
    # logo = cv2.imread('utils/logo.png')
    try:
        result = cv2.matchTemplate(image, logo, method)
    except Exception as e:
        print(f"Couldnt match template ({e})")
        return False

    # We want the minimum squared difference
    _, _, mnLoc, _ = cv2.minMaxLoc(result)

    # coordinates of the match
    MPx, MPy = mnLoc

    # Get the size of the template. This is the same size as the match.
    trows, tcols = logo.shape[:2]

    # Get the detected image and compare it with the logo to rule out false positives
    detected_image = image[MPy: MPy + trows, MPx: MPx + tcols]

    hash0 = imagehash.average_hash(Image.fromarray(logo))
    hash1 = imagehash.average_hash(Image.fromarray(detected_image))

    cutoff = 5  # maximum bits that could be different between the hashes.
    print(hash0 - hash1)
    if hash0 - hash1 <= cutoff:
        return True
    else:
        return False


def cancer_detection(source: str) -> bool:
    if not source or not source.endswith(".mp4"): raise ValueError

    vidcap = cv2.VideoCapture(source)
    _, image = vidcap.read()

    # try to match the first frame
    if cancer_detect_img(source=image):
        return True
        
    else:

        while not cancer_detect_img(image):
            _, image = vidcap.read()
            if cancer_detect_img(image, "logo"):
                return True
            if cancer_detect_img(image, "text"):
                return True


class Cancermod(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def cure_cancer(self, message):
        if message.channel not in [866382247720386591, 640223984557883413]:
            for att in message.attachments:
                if att.filename.endswith(".mp4"):
                    await att.save(att.filename)

                    if cancer_detection(att.filename):
                        try:
                            await message.delete()
                        except discord.errors.Forbidden:
                            try:
                                await message.channel.send("zamknij mordę")
                            except Exception:
                                pass
                        finally:
                            os.remove(att.filename)

        # await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(Cancermod(bot))
