import discord
from discord.ext import commands
import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

scores = {}

def is_palindrome(t):
    s = t.replace(":", "")
    return s == s[::-1]

def is_sequence(t):
    s = t.replace(":", "")
    sequences = ["1234","2345","3456","4567","5678","6789"]
    return s in sequences

def is_repeat(t):
    s = t.replace(":", "")
    return len(set(s)) == 1

@bot.event
async def on_ready():
    print("Bot is online!")

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    now = datetime.datetime.now().strftime("%H:%M")
    user_time = message.content.strip()

    if user_time == now:

        points = 0

        if is_repeat(user_time):
            points = 3
        elif is_palindrome(user_time):
            points = 2
        elif is_sequence(user_time):
            points = 1

        if points > 0:

            user = message.author.id

            if user not in scores:
                scores[user] = 0

            scores[user] += points

            await message.channel.send(
                f"{message.author.mention} got {points} points! Total: {scores[user]}"
            )

    await bot.process_commands(message)

bot.run("MTQ4MDk4MDk1NTYxNDQxMjk4Mw.G-Y88J.P12SykqY_F-Xd3CKDvqoWBOU4KvqB7sVSKttHs")
