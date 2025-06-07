
import discord
from discord.ext import commands
import json
import os
import datetime
import pytz

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True  # 별명 표시를 위해 멤버 정보 필요
bot = commands.Bot(command_prefix='!', intents=intents)

KST = pytz.timezone("Asia/Seoul")
def get_today_kst():
    return datetime.datetime.now(KST).date()

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open("data.json", "w") as f:
        json.dump({"user_data": user_data, "출석_기록": 출석_기록}, f)

data = load_data()
user_data = data.get("user_data", {})
출석_기록 = data.get("출석_기록", {})

@bot.event
async def on_ready():
    print(f'{bot.user.name} 봇이 정상 작동 중입니다.')

@bot.command()
async def 출석(ctx):
    uid = str(ctx.author.id)
    today = get_today_kst()

    if uid in 출석_기록 and 출석_기록[uid] == str(today):
        await ctx.send("이미 출석하셨습니다! 내일 다시 와주세요.")
        return

    user_data[uid] = user_data.get(uid, 0) + 100
    출석_기록[uid] = str(today)
    save_data()
    await ctx.send(f"{ctx.author.name}님 출석 완료! +100P")

@bot.command()
async def 포인트(ctx):
    uid = str(ctx.author.id)
    points = user_data.get(uid, 0)
    await ctx.send(f"{ctx.author.name}님의 보유 포인트: {points}P")

@bot.command()
async def 랭킹(ctx):
    if not user_data:
        await ctx.send("아직 데이터가 없습니다.")
        return

    top5 = sorted(user_data.items(), key=lambda x: x[1], reverse=True)[:5]
    result = []
    for uid, point in top5:
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"알 수 없음 ({uid})"
        result.append(f"{name}: {point}P")

message = "🏆 포인트 랭킹 TOP 5 🏆\n" + "\n".join(result)
await ctx.send(message)

@bot.command()
@commands.is_owner()
async def 지급(ctx, member: discord.Member, amount: int):
    uid = str(member.id)
    user_data[uid] = user_data.get(uid, 0) + amount
    save_data()
    await ctx.send(f"{member.display_name}님께 {amount}포인트 지급 완료!")

bot.run(os.getenv("TOKEN"))
