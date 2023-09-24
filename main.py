import bs4
import discord
import json
import os
import pytz
import requests
from asyncio import sleep
from datetime import datetime
from discord.ext import tasks
from ping_bot import ping_bot

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Bot command prefix
cmd_prefix = "$"
# Bot command list
cmd_list = []

# User ID values hidden and accessed through Replit Secrets (Environment variables)
ADMIN = int(os.environ['USER_ADMIN'])

# Bot authorised users
authorised_users = [ADMIN]

# Server ID
PROGRAMMING_ANNOUNCEMENT = int(os.environ['PROGRAMMING_ANNOUNCEMENT'])
PROGRAMMING_TEST_DEPLOY = int(os.environ['PROGRAMMING_TEST_DEPLOY'])
IE_WICKLOW = int(os.environ['IE_WICKLOW'])


# General bot features
def validate_response(link_target):
    if link_target.status_code == 200:
        return link_target.json()

    return False


def get_inspiration():
    inspiration = requests.get("https://zenquotes.io/api/random")
    inspiration_json = json.loads(inspiration.text)

    return inspiration_json[0]['q'] + " - " + inspiration_json[0]['a']


def get_joke():
    joke_response = requests.get("https://v2.jokeapi.dev/joke/Any")
    joke_json = validate_response(joke_response)

    for key, value in joke_json.items():
        if key == "type" and value == "twopart":
            setup = joke_json["setup"]
            punchline = joke_json["delivery"]

            return setup + "\n" + punchline
        else:
            if key == "joke":
                joke = value

                return joke


def get_compliment():
    compliment = None

    compliment_response = requests.get("https://complimentr.com/api")
    compliment_json = validate_response(compliment_response)

    for key, value in compliment_json.items():
        compliment = value

    return compliment


def get_advice():
    advice = None

    advice_response = requests.get("https://api.adviceslip.com/advice")
    advice_json = validate_response(advice_response)

    for k, v in advice_json.items():
        for key, value in v.items():
            if key == "advice":
                advice = value

    return advice


def get_prize_pool(link, selector):
    response = requests.get(link)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    element = soup.select(selector)

    return element[0].text.strip()


# Lottery Reminder
@tasks.loop(hours=24)
async def lottery_reminder():
    euro_million_draw = ["Tuesday", "Friday"]
    irish_lotto_draw = ["Wednesday", "Saturday"]

    if datetime.now().strftime("%A") in euro_million_draw:
        prize_pool = get_prize_pool("https://www.lottery.ie/draw-games/euromillions",
                                    "#__next > div > div.flex.flex-col.lg\:flex-row.w-full.h-full > "
                                    "div.flex.flex-col.lg\:flex-row.w-full.px-4.md\:px-6.lg\:pl-28.h-full.z-1 > "
                                    "div.flex.flex-col.w-full.md\:w-125.lg\:w-5\/12.mx-auto.md\:mt-9.lg\:mx-0.lg\:pr"
                                    "-14.items-between.mt-8 > div.flex.lg\:block.justify-between.flex-col > "
                                    "div.flex.flex-col > h1 > span")

        await client.get_channel(IE_WICKLOW).send(f"Today's *Euro Millions* has a **{prize_pool.rstrip('*')}**. "
                                                  f"It could be you!")

    if datetime.now().strftime("%A") in irish_lotto_draw:
        prize_pool = get_prize_pool("#__next > div > div.flex.flex-col.lg\:flex-row.w-full.h-full > "
                                    "div.flex.flex-col.lg\:flex-row.w-full.px-4.md\:px-6.lg\:pl-28.h-full.z-1 > "
                                    "div.flex.flex-col.w-full.md\:w-125.lg\:w-5\/12.mx-auto.md\:mt-9.lg\:mx-0.lg\:pr"
                                    "-14.items-between.mt-8 > div.flex.lg\:block.justify-between.flex-col > "
                                    "div.flex.flex-col > h1 > span")

        await client.get_channel(IE_WICKLOW).send(f"Today's *Irish Lotto* has a **{prize_pool.rstrip('*')}**. "
                                                  f"It could be you!")


@lottery_reminder.before_loop
async def before_lottery_reminder():
    for i in range(60 * 60 * 24):
        if datetime.now(pytz.timezone("Europe/London")).hour == 13 and datetime.now().minute == 0:
            return

        await sleep(1)


# General Reminder
@tasks.loop(minutes=15)
async def reminder():
    pass


@reminder.before_loop
async def before_reminder():
    for i in range(60 * 60 * 24):
        minutes = [0, 15, 30]
        if datetime.now().minute in minutes:
            return

        await sleep(1)


# College reminders
@tasks.loop(hours=1)
async def college_reminder():
    TIMEZONE_UK = pytz.timezone("Europe/London")
    JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER = range(1, 13)

    if datetime.now().month == SEPTEMBER and datetime.now().day == 18 and datetime.now(TIMEZONE_UK).hour == 7:
        await client.get_channel(PROGRAMMING_ANNOUNCEMENT).send(f"Classes resumes today!")


@college_reminder.before_loop
async def before_college_reminder():
    for i in range(60 * 60 * 24):
        if datetime.now().minute == 0:
            return

        await sleep(1)


# Daily Inspirational Quotes
@tasks.loop(hours=24)
async def daily_inspiration():
    await client.get_channel(IE_WICKLOW).send(get_inspiration())


@daily_inspiration.before_loop
async def before_daily_message():
    for i in range(60 * 60 * 24):
        if datetime.now(pytz.timezone("Europe/London")).hour == 9 and datetime.now().minute == 0:
            return

        await sleep(1)


# Daily Advice
@tasks.loop(hours=24)
async def daily_advice():
    await client.get_channel(IE_WICKLOW).send("**Advice:** " + get_advice())


@daily_advice.before_loop
async def before_daily_advice():
    for i in range(60 * 60 * 24):
        if datetime.now(pytz.timezone("Europe/London")).hour == 15 and datetime.now().minute == 0:
            return

        await sleep(1)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    reminder.start()  # General reminder
    lottery_reminder.start()  # Lottery reminder
    college_reminder.start()  # College reminder
    daily_inspiration.start()  # Daily quotes
    daily_advice.start()  # Daily advice

    await client.change_presence(activity=discord.Game("Discord Bot"))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    # General bot features
    cmd_inspire = f"{cmd_prefix}inspire"
    cmd_list.append(cmd_inspire)
    if msg.startswith(cmd_inspire):
        quote = get_inspiration()
        await message.channel.send(quote)

    cmd_joke = f"{cmd_prefix}joke"
    cmd_list.append(cmd_joke)
    if msg.startswith(cmd_joke):
        joke = get_joke()
        await message.channel.send(joke)

    cmd_advice = f"{cmd_prefix}advice"
    cmd_list.append(cmd_advice)
    if msg.startswith(cmd_advice):
        advice = get_advice()
        await message.channel.send(advice)

    cmd_praise = f"{cmd_prefix}praise"
    cmd_list.append(cmd_praise)
    if msg.startswith(cmd_praise):
        praise_target = msg.split(" ")
        compliment = get_compliment()
        if len(praise_target) > 1:
            praise_target = msg.split(f"{cmd_praise} ", 1)[1]
            await message.channel.send(praise_target + ", " + compliment)
        else:
            await message.channel.send(message.author.mention + ", " + compliment)

    cmd_help = f"{cmd_prefix}help"
    if msg.startswith(cmd_help):
        await message.channel.send("[Bot Commands]\n" + "\n".join(cmd_list))


ping_bot()
client.run(os.getenv("TOKEN"))
