import discord
from discord.ext import commands
import random
import json
import os
from datetime import datetime, timedelta

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"
user_data = {}

# 데이터 불러오기 및 저장
def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    else:
        user_data = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

load_data()

# 출석 명령어
@bot.command()
async def 출석(ctx):
    uid = str(ctx.author.id)
    now_kst = datetime.utcnow() + timedelta(hours=9)
    today_str = now_kst.strftime("%Y-%m-%d")
    if user_data.get(uid, {}).get("last_attendance") == today_str:
        await ctx.send(f"{ctx.author.mention} 이미 출석하셨습니다!")
    else:
        user_data.setdefault(uid, {"point": 0})
        user_data[uid]["point"] += 100
        user_data[uid]["last_attendance"] = today_str
        save_data()
        await ctx.send(f"{ctx.author.mention}님 출석 완료! +100P")

# 포인트 확인
@bot.command()
async def 포인트(ctx):
    uid = str(ctx.author.id)
    point = user_data.get(uid, {}).get("point", 0)
    await ctx.send(f"{ctx.author.mention}님의 포인트: {point}P")

# 슬롯머신
@bot.command()
async def 슬롯(ctx, 금액: int):
    uid = str(ctx.author.id)
    if 금액 <= 0 or user_data.get(uid, {}).get("point", 0) < 금액:
        await ctx.send(f"{ctx.author.mention} 포인트가 부족합니다!")
        return
    아이콘 = ["🍒", "🍋", "🍉", "⭐", "🔔"]
    결과 = [random.choice(아이콘) for _ in range(3)]
    await ctx.send("[ " + " | ".join(결과) + " ]")
    if len(set(결과)) == 1:
        당첨 = 금액 * 5
        user_data[uid]["point"] += 당첨
        메시지 = f"잭팟! +{당첨}P"
    elif len(set(결과)) == 2:
        당첨 = 금액 * 2
        user_data[uid]["point"] += 당첨
        메시지 = f"2개 일치! +{당첨}P"
    else:
        user_data[uid]["point"] -= 금액
        메시지 = f"꽝! -{금액}P"
    save_data()
    await ctx.send(f"{ctx.author.mention}님 {메시지}")

# 홀짝
@bot.command()
async def 홀짝(ctx, 선택: str, 금액: int):
    uid = str(ctx.author.id)
    if 선택 not in ["홀", "짝"] or 금액 <= 0 or user_data.get(uid, {}).get("point", 0) < 금액:
        await ctx.send(f"{ctx.author.mention} 입력 오류 또는 포인트 부족!")
        return
    결과 = random.choice(["홀", "짝"])
    if 선택 == 결과:
        user_data[uid]["point"] += 금액
        메시지 = f"정답! ({결과}) +{금액}P"
    else:
        user_data[uid]["point"] -= 금액
        메시지 = f"실패! ({결과}) -{금액}P"
    save_data()
    await ctx.send(f"{ctx.author.mention}님 {메시지}")

# 주사위 (숫자 맞히기 방식, 6배)
@bot.command()
async def 주사위(ctx, 선택: int, 금액: int):
    uid = str(ctx.author.id)
    if 선택 not in [1, 2, 3, 4, 5, 6] or 금액 <= 0:
        await ctx.send("잘못된 입력입니다. 예: !주사위 6 1000")
        return
    if user_data.get(uid, {}).get("point", 0) < 금액:
        await ctx.send(f"{ctx.author.mention} 포인트가 부족합니다!")
        return
    결과 = random.randint(1, 6)
    if 선택 == 결과:
        당첨 = 금액 * 6
        user_data[uid]["point"] += 당첨
        메시지 = f"🎯 정답! {결과} 🎉 +{당첨}P"
    else:
        user_data[uid]["point"] -= 금액
        메시지 = f"❌ 꽝! 나온 숫자: {결과} -{금액}P"
    save_data()
    await ctx.send(f"{ctx.author.mention}님 {메시지}")

# 경마
@bot.command()
async def 경마(ctx, 번호: int, 금액: int):
    uid = str(ctx.author.id)
    if 번호 not in [1, 2, 3, 4] or 금액 <= 0:
        await ctx.send("잘못된 입력입니다. 예: !경마 2 1000")
        return
    if user_data.get(uid, {}).get("point", 0) < 금액:
        await ctx.send(f"{ctx.author.mention} 포인트가 부족합니다!")
        return
    우승 = random.randint(1, 4)
    if 번호 == 우승:
        당첨 = 금액 * 3
        user_data[uid]["point"] += 당첨
        메시지 = f"🎉 우승 말: {우승}번! +{당첨}P"
    else:
        user_data[uid]["point"] -= 금액
        메시지 = f"❌ 우승 말: {우승}번! -{금액}P"
    save_data()
    await ctx.send(f"{ctx.author.mention}님 {메시지}")

# 포인트 랭킹
@bot.command()
async def 랭킹(ctx):
    if not user_data:
        await ctx.send("포인트 데이터가 없습니다.")
        return
    랭킹 = sorted(user_data.items(), key=lambda x: x[1].get("point", 0), reverse=True)[:5]
    result = []
    for uid, info in 랭킹:
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"User({uid})"
        result.append(f"{name}: {info['point']}P")
    메시지 = "🏆 포인트 랭킹 TOP 5 🏆\n" + "\n".join(result)
    await ctx.send(메시지)

# 봇 실행
@bot.event
async def on_ready():
    print("✅ 요트봇 봇이 정상 작동 중입니다.")

# 환경 변수나 토큰 설정은 여기서
bot.run("YOUR_DISCORD_BOT_TOKEN")
