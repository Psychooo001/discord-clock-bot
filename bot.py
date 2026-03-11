import discord
from discord.ext import commands
import datetime
import os
import random
import re

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

scores = {}
last_claim = {}
clock_channels = {}

wrong_messages = [
    "Oh! Time mismatched. Are you late or trying to cheat? 👀",
    "That clock doesn't look right 🤔",
    "Nice try... but the time doesn't match ⏰",
    "Oops! That's not the correct time."
]

# detect if message looks like time
def is_time_message(msg):
    return bool(re.fullmatch(r"\d{1,2}:\d{2}|\d{3,4}", msg))


# generate all valid time formats
def generate_valid_times(now):

    h24 = now.strftime("%H")
    h12 = now.strftime("%I").lstrip("0")
    m = now.strftime("%M")

    formats = set()

    formats.add(f"{h24}:{m}")
    formats.add(f"{h12}:{m}")

    formats.add(f"{h24}{m}")
    formats.add(f"{h12}{m}")

    formats.add(f"{int(h24)}{m}")
    formats.add(f"{int(h12)}{m}")

    return formats


# detect patterns
def check_pattern(time_str):

    t = time_str.replace(":", "")
    digits = [int(d) for d in t]

    if len(set(digits)) == 1:
        return 3

    if digits == digits[::-1]:
        return 2

    if all(digits[i] + 1 == digits[i+1] for i in range(len(digits)-1)):
        return 1

    if all(digits[i] - 1 == digits[i+1] for i in range(len(digits)-1)):
        return 1

    return 0


@bot.event
async def on_ready():
    print(f"{bot.user} is online!")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None

    if guild_id not in clock_channels:
        await bot.process_commands(message)
        return

    if message.channel.id != clock_channels[guild_id]:
        await bot.process_commands(message)
        return

    user_input = message.content.strip()

    # ignore messages that are not time
    if not is_time_message(user_input):
        await bot.process_commands(message)
        return

    now = datetime.datetime.now()
    valid_inputs = generate_valid_times(now)

    if user_input not in valid_inputs:

        scores[message.author.id] = scores.get(message.author.id, 0) - 1

        await message.add_reaction("❌")

        await message.channel.send(
            f"{message.author.mention} {random.choice(wrong_messages)}"
        )

        return

    minute_key = now.strftime("%Y-%m-%d %H:%M")

    if message.author.id in last_claim:
        if last_claim[message.author.id] == minute_key:
            return

    last_claim[message.author.id] = minute_key

    points = check_pattern(now.strftime("%H:%M"))

    if points == 0:
        return

    scores[message.author.id] = scores.get(message.author.id, 0) + points

    await message.add_reaction("✅")

    if points == 1:
        await message.add_reaction("1️⃣")
    elif points == 2:
        await message.add_reaction("2️⃣")
    elif points == 3:
        await message.add_reaction("3️⃣")

    await bot.process_commands(message)


# set clock channel
@bot.command()
@commands.has_permissions(administrator=True)
async def setclock(ctx):

    clock_channels[ctx.guild.id] = ctx.channel.id

    await ctx.send("⏰ This channel is now the clock channel!")


# leaderboard
@bot.command()
async def clockscore(ctx):

    if not scores:
        await ctx.send("No scores yet.")
        return

    leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    msg = "**Clock Leaderboard**\n"

    for user_id, score in leaderboard[:10]:
        user = await bot.fetch_user(user_id)
        msg += f"{user.name}: {score}\n"

    await ctx.send(msg)


bot.run(os.getenv("TOKEN"))
