#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💜 자이(JAI) Discord 봇
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Discord 서버에서 모든 대화를 학습하는 AI 봇

핵심 기능:
1. 📖 모든 채널 메시지 자동 수집 및 학습
2. 💬 자이와 직접 대화 (/jai 명령어)
3. 📊 실시간 트렌드 분석 및 공유
4. 🎤 음성 채널 참여 (향후)
5. 🖼️ 화면 공유 감지 및 OCR (향후)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime
import re

# 자이의 기존 시스템 임포트
from jai_memory_system import (
    get_or_create_user_profile,
    learn_from_conversation,
    save_conversation,
    build_user_context,
    get_personalized_greeting,
    get_relationship_level
)

from jai_learning_system import (
    TwitterLearner,
    TrendAnalyzer,
    AISimulator
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 Discord 봇 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Intents 설정 (모든 메시지 읽기 권한)
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용 읽기
intents.members = True          # 멤버 정보 읽기
intents.guilds = True           # 서버 정보 읽기
intents.voice_states = True     # 음성 채널 상태

# 봇 생성
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    description='💜 자이(JAI) - AI 트레이딩 어시스턴트'
)

# 학습 시스템 초기화
twitter_learner = TwitterLearner()
trend_analyzer = TrendAnalyzer()
ai_simulator = AISimulator()

# 통계 추적
stats = {
    'messages_learned': 0,
    'users_tracked': set(),
    'channels_monitored': set(),
    'coins_detected': {},
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📡 이벤트 핸들러
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.event
async def on_ready():
    """봇 시작 시"""
    print(f"""
╔═══════════════════════════════════════════════╗
║   💜 자이(JAI) Discord 봇 시작!              ║
╚═══════════════════════════════════════════════╝

✅ 봇 이름: {bot.user.name}
✅ 봇 ID: {bot.user.id}
✅ 서버 수: {len(bot.guilds)}
✅ 모니터링 시작!

명령어:
  !jai <메시지>  - 자이와 대화
  !트렌드         - 현재 코인 트렌드
  !통계          - 학습 통계
  !도움말        - 전체 명령어
""")
    
    # 봇 상태 메시지
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="코인 시장 📊 | !jai"
        )
    )

@bot.event
async def on_message(message):
    """모든 메시지 자동 학습"""
    
    # 봇 자신의 메시지는 무시
    if message.author.bot:
        return
    
    # 명령어 먼저 처리
    await bot.process_commands(message)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📚 자동 학습 시작
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    content = message.content
    user_id = str(message.author.id)
    username = message.author.name
    
    # 1️⃣ 사용자 프로필 생성/업데이트
    profile = get_or_create_user_profile(user_id, username)
    
    # 2️⃣ 대화에서 자동 학습
    learned_info = learn_from_conversation(user_id, username, content)
    
    # 3️⃣ 코인 관련 메시지면 패턴 학습
    if is_crypto_related(content):
        pattern_id = twitter_learner.learn_from_text(
            text=content,
            source_id=f"discord_{message.guild.id}_{message.channel.id}",
            engagement=len(message.reactions)
        )
        
        # 코인 카운팅
        coins = extract_coins(content)
        for coin in coins:
            stats['coins_detected'][coin] = stats['coins_detected'].get(coin, 0) + 1
        
        stats['messages_learned'] += 1
    
    # 4️⃣ 통계 업데이트
    stats['users_tracked'].add(user_id)
    stats['channels_monitored'].add(f"{message.guild.name}#{message.channel.name}")
    
    # 5️⃣ 중요한 정보면 자이가 자동 응답
    if should_jai_respond(content):
        async with message.channel.typing():
            response = await generate_jai_response(user_id, username, content)
            await message.reply(response)

def is_crypto_related(text):
    """암호화폐 관련 메시지 감지"""
    crypto_keywords = [
        '비트코인', 'BTC', '이더리움', 'ETH', '리플', 'XRP',
        '코인', '암호화폐', '가상화폐', '매수', '매도',
        '상승', '하락', '떡상', '폭락', '차트', '투자'
    ]
    return any(keyword.lower() in text.lower() for keyword in crypto_keywords)

def extract_coins(text):
    """텍스트에서 코인 추출"""
    coins = []
    coin_patterns = {
        'BTC': r'비트코인|bitcoin|btc',
        'ETH': r'이더리움|ethereum|eth',
        'XRP': r'리플|ripple|xrp',
        'SOL': r'솔라나|solana|sol',
        'ADA': r'에이다|cardano|ada',
    }
    
    for coin, pattern in coin_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            coins.append(coin)
    
    return coins

def should_jai_respond(text):
    """자이가 자동 응답해야 하는지 판단"""
    # 자이를 직접 멘션하거나 질문하는 경우
    trigger_words = ['자이', 'jai', '추천', '어떻게', '분석', '예상']
    return any(word in text.lower() for word in trigger_words)

async def generate_jai_response(user_id, username, message):
    """자이의 맞춤 응답 생성"""
    # 사용자 컨텍스트
    context = build_user_context(user_id, username)
    real_name = get_user_real_name(user_id)
    display_name = real_name if real_name else username
    
    # 트렌드 분석 데이터
    trending = trend_analyzer.get_trending_coins(top_n=3)
    
    # 간단한 응답 (OpenAI API 없이도 작동)
    if '트렌드' in message or '추천' in message:
        if trending:
            response = f"{display_name}님, 지금 핫한 코인은:\n"
            for rank, item in enumerate(trending, 1):
                response += f"{rank}. {item['coins']} ({item['mentions']}회 언급)\n"
            response += "\n더 자세한 분석은 `!jai 분석해줘` 로 물어보세요! 💜"
        else:
            response = f"{display_name}님, 아직 학습 데이터가 부족해요. 조금만 기다려주세요!"
    else:
        response = f"{display_name}님! 무엇이 궁금하신가요? 💜"
    
    return response

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎮 명령어
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.command(name='jai', aliases=['자이'])
async def jai_chat(ctx, *, message: str):
    """자이와 대화하기"""
    user_id = str(ctx.author.id)
    username = ctx.author.name
    
    async with ctx.typing():
        # 프로필 로드
        profile = get_or_create_user_profile(user_id, username)
        
        # 학습
        learned = learn_from_conversation(user_id, username, message)
        
        # 응답 생성
        response = await generate_jai_response(user_id, username, message)
        
        # 대화 저장
        save_conversation(user_id, username, message, response)
        
        # 임베드로 예쁘게 표시
        embed = discord.Embed(
            title="💜 자이(JAI)",
            description=response,
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url="https://www.genspark.ai/api/files/s/3xEhfRCY")
        
        if learned:
            embed.add_field(
                name="📚 학습 완료",
                value=f"```{learned}```",
                inline=False
            )
        
        await ctx.reply(embed=embed)

@bot.command(name='트렌드', aliases=['trend'])
async def show_trends(ctx):
    """현재 트렌딩 코인"""
    trending = trend_analyzer.get_trending_coins(top_n=5)
    
    embed = discord.Embed(
        title="🔥 현재 트렌딩 코인",
        description="Discord에서 가장 많이 언급된 코인들",
        color=discord.Color.gold()
    )
    
    if trending:
        for rank, item in enumerate(trending, 1):
            embed.add_field(
                name=f"{rank}. {item['coins']}",
                value=f"언급: {item['mentions']}회\n신뢰도: {item['confidence']:.2%}",
                inline=True
            )
    else:
        embed.description = "아직 데이터가 충분하지 않아요. 조금만 기다려주세요!"
    
    await ctx.send(embed=embed)

@bot.command(name='통계', aliases=['stats'])
async def show_stats(ctx):
    """학습 통계"""
    embed = discord.Embed(
        title="📊 자이의 학습 통계",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="💬 학습한 메시지",
        value=f"{stats['messages_learned']}개",
        inline=True
    )
    
    embed.add_field(
        name="👥 추적 중인 사용자",
        value=f"{len(stats['users_tracked'])}명",
        inline=True
    )
    
    embed.add_field(
        name="📺 모니터링 채널",
        value=f"{len(stats['channels_monitored'])}개",
        inline=True
    )
    
    if stats['coins_detected']:
        top_coins = sorted(
            stats['coins_detected'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        coins_text = "\n".join([f"{coin}: {count}회" for coin, count in top_coins])
        embed.add_field(
            name="🪙 가장 많이 언급된 코인",
            value=f"```{coins_text}```",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='분석', aliases=['analyze'])
async def analyze_coin(ctx, coin: str):
    """특정 코인 트렌드 분석"""
    coin = coin.upper()
    
    async with ctx.typing():
        trend = trend_analyzer.analyze_coin_trend(coin, '1h')
        
        if trend:
            embed = discord.Embed(
                title=f"📊 {coin} 트렌드 분석",
                color=discord.Color.green() if trend['trend_direction'] == 'bullish' else discord.Color.red()
            )
            
            embed.add_field(
                name="📈 방향",
                value=trend['trend_direction'].upper(),
                inline=True
            )
            
            embed.add_field(
                name="💬 언급 횟수",
                value=f"{trend['mention_count']}회",
                inline=True
            )
            
            embed.add_field(
                name="✅ 신뢰도",
                value=f"{trend['confidence']:.2%}",
                inline=True
            )
            
            embed.add_field(
                name="😊 감정 분석",
                value=f"긍정: {trend['sentiment_breakdown']['positive']}\n"
                      f"부정: {trend['sentiment_breakdown']['negative']}\n"
                      f"중립: {trend['sentiment_breakdown']['neutral']}",
                inline=False
            )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ {coin}에 대한 데이터가 충분하지 않아요.")

@bot.command(name='도움말', aliases=['help', 'commands'])
async def show_help(ctx):
    """명령어 도움말"""
    embed = discord.Embed(
        title="💜 자이(JAI) 명령어",
        description="사용 가능한 모든 명령어",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="!jai <메시지>",
        value="자이와 대화하기\n예: `!jai 비트코인 어때?`",
        inline=False
    )
    
    embed.add_field(
        name="!트렌드",
        value="현재 핫한 코인 확인",
        inline=False
    )
    
    embed.add_field(
        name="!분석 <코인>",
        value="특정 코인 트렌드 분석\n예: `!분석 BTC`",
        inline=False
    )
    
    embed.add_field(
        name="!통계",
        value="자이의 학습 통계 확인",
        inline=False
    )
    
    embed.add_field(
        name="✨ 자동 학습",
        value="자이는 모든 대화를 자동으로 학습합니다!\n"
              "코인 관련 대화를 하면 자동으로 패턴을 분석해요.",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎤 음성 채널 이벤트 (향후 구현)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.event
async def on_voice_state_update(member, before, after):
    """음성 채널 상태 변화 감지"""
    
    # 화면 공유 시작 감지
    if after.self_stream and not before.self_stream:
        print(f"🖥️ {member.name}님이 화면 공유 시작!")
        # TODO: 화면 공유 내용 OCR 분석
    
    # 음성 채널 입장
    if after.channel and not before.channel:
        print(f"🎤 {member.name}님이 {after.channel.name} 입장!")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 봇 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    # Discord 봇 토큰 (환경변수에서 읽기)
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if not TOKEN:
        print("""
❌ Discord 봇 토큰이 설정되지 않았습니다!

설정 방법:
1. Discord Developer Portal에서 봇 생성
   https://discord.com/developers/applications

2. Bot 탭에서 토큰 복사

3. 환경변수 설정
   export DISCORD_BOT_TOKEN='your-token-here'

4. 봇 초대 링크 생성 (필요한 권한)
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Read Message History
   - Add Reactions
   - Connect (Voice)
   - Speak (Voice)
""")
    else:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"❌ 봇 실행 오류: {e}")
