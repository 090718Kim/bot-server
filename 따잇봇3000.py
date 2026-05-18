import discord
import re
import datetime 
import asyncio
from flask import Flask
from threading import Thread

# 가짜 웹사이트 구동기 (Flask)
app = Flask('')

@app.route('/')
def home():
    return "영제따잇봇1337 24시간 가동 중... (감시망 이상 무)"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True 
intents.reactions = True 

client = discord.Client(intents=intents)

LOG_CHANNEL_ID = 1502593842283679935  

@client.event
async def on_ready():
    print(f'[{client.user.name}] 영제따잇봇 버전 1337 준비완료. (웹 서버 가동)')

# 이스터에그 (주석처리됨)
# @client.event
# async def on_message(message):
#     if message.author.bot:
#         return
#
#     if message.content == '!비상':
#         log_channel = client.get_channel(LOG_CHANNEL_ID)
#         if log_channel:
#             now = datetime.datetime.now()
#             time_str = now.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
#             embed = discord.Embed(
#                 title="🇨🇳 특급 보안 경보 🇨🇳",
#                 description=f"## 🇨🇳 경고 🇨🇳\n\n현재 시간 **{time_str}** 경,\n**영제의 중국(IP/물리적) 방문을 탐지함.**\n\n국가 보안 및 서버 안전을 위해 아래 대처 요령을 즉각 숙지할 것.",
#                 color=0xFF0000
#             )
#             guidelines = (
#                 "• **VPN 필수:** 즉시 미국 또는 안전 국가로 VPN 우회 설정\n"
#                 "• **네트워크 차단:** 영제 핫스팟 및 검증되지 않은 공공 Wi-Fi 절대 사용 금지\n"
#                 "• **물리적 보안:** 휴대폰, 컴퓨터 등 카메라 기능이 있는 기기의 렌즈 즉각 가리기\n"
#                 "• **브라우징 주의:** 보안(HTTPS)이 검증된 페이지만 이용하기\n"
#                 "• **앱 강제 종료:** 틱톡, 알리익스프레스, 테무(Temu) 등 의심 앱 즉시 삭제\n"
#                 "• **클릭 금지:** 알 수 없는 한자 팝업 등장 시 절대 **'同意(동의)'** 누르지 않기\n"
#                 "• **비상 탈출:** 평소보다 핑(Ping)이 튀거나 마우스가 혼자 움직이면 즉시 랜선 뽑기"
#             )
#             embed.add_field(name="⚠️ 영제 중국 방문 시 대처 요령 ⚠️", value=guidelines, inline=False)
#             embed.set_footer(text="이 메시지는 [영제따잇봇] 관리자 긴급명령에 의해 발송됨.")
#             
#             await log_channel.send(content="@everyone", embed=embed)
#             print("[알림] 🇨🇳 영제 중국 방문 경고 메시지 발송 완료 🇨🇳")

# 1. 채팅삭제
@client.event
async def on_message_delete(message):
    if message.author.bot or message.channel.id == LOG_CHANNEL_ID:
        return
        
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    embed = discord.Embed(
        title="🖕 메시지 삭제 감지 🖕",
        description=f"**{message.author.name}** 이/가 <#{message.channel.id}> 에서 무언가를 삭제함.",
        color=0xFF0000,
        timestamp=discord.utils.utcnow()
    )

    if message.content:
        gif_url = None
        urls = re.findall(r"(https?://[^\s]+)", message.content)
        for url in urls:
            if "tenor.com" in url or "klipy.com" in url or url.endswith(('.gif', '.png', '.jpg')):
                gif_url = url
                break

        embed.add_field(name="🖕 삭제된 내용 🖕", value=message.content, inline=False)
        if gif_url:
            embed.set_image(url=gif_url)

    if message.attachments:
        try:
            files = []
            for att in message.attachments:
                file = await att.to_file(spoiler=False)
                files.append(file)
                if att.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    embed.set_image(url=f"attachment://{att.filename}")
                    
            await log_channel.send(files=files, embed=embed)
            return
        except Exception as e:
            embed.add_field(name="🖕 로딩 실패 🖕", value="첨부파일이 너무 빨리 파기됨.", inline=False)

    await log_channel.send(embed=embed)

# 2. 채팅을 수정했을 때
@client.event
async def on_message_edit(before, after):
    if before.author.bot or before.channel.id == LOG_CHANNEL_ID:
        return
        
    if before.content == after.content and len(before.attachments) == len(after.attachments):
        return

    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    embed = discord.Embed(
        title="🖕 메시지 수정 감지 🖕",
        description=f"**{after.author.name}** 이/가 <#{after.channel.id}> 에서 수정함.",
        color=0xFFA500,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(name="🖕 수정 전 🖕", value=before.content or "(내용 없음)", inline=False)
    embed.add_field(name="🖕 수정 후 🖕", value=after.content or "(내용 없음)", inline=False)

    if len(before.attachments) > len(after.attachments):
        embed.add_field(name="🖕 첨부파일 삭제 감지 🖕", value="글은 놔두고 파일(사진)만 지움", inline=False)
        removed_attachments = [a for a in before.attachments if a not in after.attachments]
        
        if removed_attachments:
            try:
                files = []
                for att in removed_attachments:
                    file = await att.to_file(spoiler=False)
                    files.append(file)
                    if att.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) and not embed.image:
                        embed.set_image(url=f"attachment://{att.filename}")
                await log_channel.send(embed=embed, files=files)
                return
            except Exception as e:
                embed.add_field(name="🖕 첨부파일 로딩 실패 🖕", value="삭제된 파일을 건져내지 못함.", inline=False)

    await log_channel.send(embed=embed)

# 3. 반응을 취소했을 때
@client.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == client.user.id:
        return
        
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    user = client.get_user(payload.user_id)
    if not user:
        user = await client.fetch_user(payload.user_id)
        
    if user.bot:
        return

    channel = client.get_channel(payload.channel_id)
    if not channel:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
        original_content = message.content or "(내용 없음 / 사진 또는 파일)"
    except discord.NotFound:
        original_content = "(원본 메시지도 이미 삭제됨)"

    embed = discord.Embed(
        title="🖕 반응(이모지) 취소 감지 🖕",
        description=f"**{user.name}** 이/가 <#{channel.id}> 에서 흔적을 지움.",
        color=0xFFFF00, 
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(name="🖕 지워버린 반응 🖕", value=str(payload.emoji), inline=False)
    embed.add_field(name="🖕 반응한 메시지 🖕", value=original_content, inline=False)

    await log_channel.send(embed=embed)


# 가짜 웹사이트 가동
keep_alive()

# 토큰
TOKEN = "MTQ5MjE5NzA0MDA2MTQxOTUzMA.GvJx04.BlohdoYu_SEn4BmbpuVhAeoNm9Y8fnbBbFqjp0"

client.run(TOKEN)
