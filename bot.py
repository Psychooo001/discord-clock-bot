import discord
from discord.ext import commands
import datetime
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

scores = {}
last_claim = {}

CLOCK_CHANNEL_ID = 1234567890  # replace with your clock channel ID


def check_pattern(time_str):
    t = time_str.replace(":", "")

    # repeating numbers
    if len(set(t)) == 1:
        return 3

    # palindrome
    if t == t[::-1]:
        return 2

    # sequence
    seq = "0123456789"
    if t in seq:
        return 1

    return 0


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id != CLOCK_CHANNEL_ID:
        return

    now = datetime.datetime.now()

    current_24 = now.strftime("%H:%M")
    current_12 = now.strftime("%I:%M").lstrip("0")

    valid_inputs = [
        current_24,
        current_12,
        current_24.replace(":", ""),
        current_12.replace(":", "")
    ]

    user_input = message.content.strip()

    # ❌ Wrong time
    if user_input not in valid_inputs:

        scores[message.author.id] = scores.get(message.author.id, 0) - 1

        await message.add_reaction("❌")

        return

    # anti spam
    minute_key = now.strftime("%Y-%m-%d %H:%M")

    if message.author.id in last_claim:
        if last_claim[message.author.id] == minute_key:
            return

    last_claim[message.author.id] = minute_key

    points = check_pattern(current_24)

    if points == 0:
        return

    scores[message.author.id] = scores.get(message.author.id, 0) + points

    # ✅ reaction
    await message.add_reaction("✅")

    # point reactions
    if points == 1:
        await message.add_reaction("1️⃣")

    elif points == 2:
        await message.add_reaction("2️⃣")

    elif points == 3:
        await message.add_reaction("3️⃣")

    await bot.process_commands(message)


@bot.command()
async def clock(ctx):

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
