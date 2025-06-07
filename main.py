import discord
from discord.ext import commands
import json
import os
import datetime
import pytz
import random

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True
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
    await ctx.send(f"{ctx.author.display_name}님 출석 완료! +100P")

@bot.command()
async def 포인트(ctx):
    uid = str(ctx.author.id)
    points = user_data.get(uid, 0)
    await ctx.send(f"{ctx.author.display_name}님의 보유 포인트: {points}P")

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

@bot.command()
async def 슬롯(ctx, 금액: int):
    uid = str(ctx.author.id)
    if user_data.get(uid, 0) < 금액 or 금액 <= 0:
        await ctx.send("포인트가 부족하거나 잘못된 금액입니다.")
        return
    그림 = ["🍒", "🍋", "🍉", "⭐", "💎"]
    결과 = [random.choice(그림) for _ in range(3)]
    메시지 = " ".join(결과)
    if 결과.count(결과[0]) == 3:
        수익 = 금액 * 5
        user_data[uid] += 수익
        결과메시지 = f"잭팟! +{수익}P"
    elif len(set(결과)) == 2:
        수익 = 금액 * 2
        user_data[uid] += 수익
        결과메시지 = f"2개 일치! +{수익}P"
    else:
        user_data[uid] -= 금액
        결과메시지 = f"실패... -{금액}P"
    save_data()
    await ctx.send(f"{메시지}\n{ctx.author.display_name}님 {결과메시지}")

@bot.command()
async def 주사위(ctx, 금액: int):
    uid = str(ctx.author.id)
    if user_data.get(uid, 0) < 금액 or 금액 <= 0:
        await ctx.send("포인트가 부족하거나 잘못된 금액입니다.")
        return
    유저눈 = random.randint(1, 6)
    봇눈 = random.randint(1, 6)
    if 유저눈 > 봇눈:
        user_data[uid] += 금액
        결과 = f"🎉 승리! +{금액}P"
    elif 유저눈 < 봇눈:
        user_data[uid] -= 금액
        결과 = f"😢 패배... -{금액}P"
    else:
        결과 = "🤝 무승부! 포인트 변화 없음."
    save_data()
    await ctx.send(f"🎲 {ctx.author.display_name}의 주사위: {유저눈} vs 봇: {봇눈}\n{결과}")

@bot.command()
async def 홀짝(ctx, 선택: str, 금액: int):
    uid = str(ctx.author.id)
    if user_data.get(uid, 0) < 금액 or 금액 <= 0 or 선택 not in ["홀", "짝"]:
        await ctx.send("잘못된 입력입니다. 예: !홀짝 홀 100")
        return
    결과 = random.choice(["홀", "짝"])
    if 선택 == 결과:
        user_data[uid] += 금액
        메시지 = f"정답! +{금액}P"
    else:
        user_data[uid] -= 금액
        메시지 = f"틀렸습니다. -{금액}P"
    save_data()
    await ctx.send(f"🌓 결과: {결과}\n{ctx.author.display_name}님 {메시지}")

@bot.command()
async def 경마(ctx, 말번호: int, 금액: int):
    uid = str(ctx.author.id)
    if 말번호 not in [1,2,3,4] or 금액 <= 0:
        await ctx.send("형식: !경마 3 100 (1~4번 말 중 하나 선택)")
        return
    if user_data.get(uid, 0) < 금액:
        await ctx.send("포인트가 부족합니다.")
        return
    승자 = random.randint(1, 4)
    결과메시지 = f"🏁 결승선 도착: 🐎{승자}번"
    if 말번호 == 승자:
        보상 = 금액 * 3
        user_data[uid] += 보상
        결과메시지 += f"\n{ctx.author.display_name}님 {말번호}번말 적중! +{보상}P"
    else:
        user_data[uid] -= 금액
        결과메시지 += f"\n{ctx.author.display_name}님 {말번호}번말 실패... -{금액}P"
    save_data()
    await ctx.send(결과메시지)

bot.run(os.getenv("TOKEN"))
