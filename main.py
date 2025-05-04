# main.py

import os
import random
import asyncio
import requests
from dotenv import load_dotenv
import discord
from discord.ext import commands

# ─── Configuração Centralizada ───────────────────────────
class Config:
    load_dotenv()
    DISCORD_TOKEN        = os.getenv("DISCORD_TOKEN")
    PANDASCORE_TOKEN     = os.getenv("PANDASCORE_TOKEN")
    TWITCH_CLIENT_ID     = os.getenv("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
    PANDASCORE_BASE_URL  = "https://api.pandascore.co/csgo"
    TWITCH_OAUTH_URL     = "https://id.twitch.tv/oauth2/token"
    TWITCH_STREAMS_URL   = "https://api.twitch.tv/helix/streams"
    SHOP_BASE_URL        = "https://www.furia.gg"
    STATIC_HISTORY       = [
        "2025-04-08 – **FURIA** 0–2 **The MongolZ** (PGL Bucharest 2025)",
        "2025-04-07 – **FURIA** 0–2 **Virtus.pro** (PGL Bucharest 2025)",
        "2025-04-06 – **FURIA** 1–2 **Complexity** (PGL Bucharest 2025)"
    ]
    SHOP_CATEGORIES = {
        "👕 Camisetas":    f"{SHOP_BASE_URL}/produtos/vestuario/camisetas",
        "🧢 Bonés":         f"{SHOP_BASE_URL}/produtos/acessorios/bones",
        "🎧 Acessórios":    f"{SHOP_BASE_URL}/produtos/acessorios"
    }

# ─── Serviços de Dados ────────────────────────────────────
def get_furia_team_id():
    token = Config.PANDASCORE_TOKEN
    if not token:
        return None
    try:
        resp = requests.get(
            f"{Config.PANDASCORE_BASE_URL}/teams",
            headers={"Authorization": f"Bearer {token}"},
            params={"search[name]": "furia"}
        )
        resp.raise_for_status()
        for team in resp.json():
            if "furia" in team.get("name", "").lower():
                return team["id"]
    except requests.RequestException:
        pass
    return None

FURIA_ID = get_furia_team_id()

def fetch_live_match():
    token = Config.PANDASCORE_TOKEN
    if not (token and FURIA_ID):
        return None
    try:
        resp = requests.get(
            f"{Config.PANDASCORE_BASE_URL}/matches",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "filter[status]":    "running",
                "filter[opponents]": FURIA_ID,
                "sort":              "begin_at",
                "page[size]":        1
            }
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        m = data[0]
        teams  = [o["opponent"]["name"] for o in m["opponents"]]
        scores = [r["score"]                  for r in m["results"]]
        if len(teams) >= 2 and len(scores) >= 2:
            return {
                "match_name": m.get("name", "Partida ao vivo"),
                "team1":      teams[0],
                "team2":      teams[1],
                "score1":     scores[0],
                "score2":     scores[1]
            }
    except requests.RequestException:
        pass
    return None

def fetch_upcoming_matches(limit=5):
    token = Config.PANDASCORE_TOKEN
    if not (token and FURIA_ID):
        return []
    try:
        resp = requests.get(
            f"{Config.PANDASCORE_BASE_URL}/matches",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "filter[status]":    "not_started",
                "filter[opponents]": FURIA_ID,
                "sort":              "begin_at",
                "page[size]":        limit
            }
        )
        resp.raise_for_status()
        upcoming = []
        for m in resp.json():
            teams = [o["opponent"]["name"] for o in m["opponents"]]
            if len(teams) >= 2:
                upcoming.append({
                    "date":       (m.get("begin_at") or "")[:16].replace("T", " "),
                    "match_name": m.get("name", ""),
                    "team1":      teams[0],
                    "team2":      teams[1]
                })
        return upcoming
    except requests.RequestException:
        pass
    return []

def fetch_recent_results(limit=3):
    return Config.STATIC_HISTORY[:limit]

def get_twitch_token():
    cid    = Config.TWITCH_CLIENT_ID
    secret = Config.TWITCH_CLIENT_SECRET
    if not (cid and secret):
        return None
    try:
        resp = requests.post(
            Config.TWITCH_OAUTH_URL,
            params={
                "client_id":     cid,
                "client_secret": secret,
                "grant_type":    "client_credentials"
            }
        )
        resp.raise_for_status()
        return resp.json().get("access_token")
    except requests.RequestException:
        return None

def fetch_stream_link(channel_name="furia"):
    token = get_twitch_token()
    if not token:
        return None
    try:
        resp = requests.get(
            Config.TWITCH_STREAMS_URL,
            headers={
                "Client-ID":     Config.TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {token}"
            },
            params={"user_login": channel_name}
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            return None
        s = data[0]
        title = s.get("title", "")
        thumb = s.get("thumbnail_url", "").replace("{width}", "320").replace("{height}", "180")
        url   = f"https://twitch.tv/{channel_name}"
        return title, thumb, url
    except requests.RequestException:
        return None

# ─── Setup do Bot ────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Comando não reconhecido. Use `!ajuda`.")
    else:
        raise error

# ─── Comandos ───────────────────────────────────────────
@bot.command(name="start")
async def start(ctx):
    embed = discord.Embed(
        title="Fala, guerreiro(a)! 🖤🔥",
        description="Aqui é o Contato Inteligente da FURIA! 👊\n\nEscolha uma opção:",
        color=0xE50914
    )
    embed.add_field(
        name="🎯 Funções",
        value=(
            "`!status` – Placar ao vivo\n"
            "`!proximos` – Próximos jogos\n"
            "`!resultados` – Resultados recentes\n"
            "`!alerta` – Alerta de início de jogo\n"
            "`!votar <nome>` – Votar no MVP\n"
            "`!clip` – Highlight aleatório\n"
            "`!ping` – Testar latência\n"
            "`!stream` – Onde assistir ao vivo\n"
            "`!loja` – Abrir loja oficial\n"
            "`!ajuda` – Ver todos os comandos"
        ),
        inline=False
    )
    embed.add_field(
        name="📜 Termos de Uso",
        value="[Leia e aceite aqui](https://terms.furia.gg/)",
        inline=False
    )
    embed.set_footer(text="Digite `!aceito` para aceitar os termos e continuar")
    await ctx.send(embed=embed)

@bot.command(name="aceito")
async def aceito(ctx):
    await ctx.send(
        "✅ Termos aceitos! Agora você pode usar:\n"
        "`!status`, `!proximos`, `!resultados`, `!alerta`, "
        "`!votar <nome>`, `!clip`, `!ping`, `!stream`, `!loja`, `!ajuda`"
    )

@bot.command(name="status")
async def status(ctx):
    live = fetch_live_match()
    if live:
        embed = discord.Embed(
            title="🔫 Partida ao vivo",
            description=(
                f"**{live['team1']}** {live['score1']}–{live['score2']} **{live['team2']}**\n"
                f"*{live['match_name']}*"
            ),
            color=0x00FF00
        )
    else:
        embed = discord.Embed(
            title="🔫 Partida ao vivo",
            description="No momento não há partidas da FURIA em andamento.",
            color=0xFF0000
        )
    await ctx.send(embed=embed)

@bot.command(name="proximos")
async def proximos(ctx):
    games = fetch_upcoming_matches(limit=5)
    if games:
        embed = discord.Embed(title="📅 Próximos Jogos da FURIA", color=0xE50914)
        for g in games:
            embed.add_field(
                name=g["match_name"],
                value=f"Quando: {g['date']}\n{g['team1']} vs {g['team2']}",
                inline=False
            )
    else:
        embed = discord.Embed(
            title="📅 Próximos Jogos da FURIA",
            description="Nenhum jogo agendado nos próximos dias.",
            color=0xFF0000
        )
    await ctx.send(embed=embed)

@bot.command(name="resultados")
async def resultados(ctx):
    hist = fetch_recent_results(limit=3)
    embed = discord.Embed(
        title="🏆 Resultados Recentes",
        description="\n".join(hist),
        color=0xFFD700
    )
    await ctx.send(embed=embed)

@bot.command(name="alerta")
async def alerta(ctx):
    proximos_jogo = fetch_upcoming_matches(limit=1)
    if not proximos_jogo:
        # Demo estático se não houver próximos reais
        jogo = {"date": "2025-05-06 18:00", "match_name": "FURIA vs ENCE (DEMO)"}
    else:
        jogo = proximos_jogo[0]
    data_hora  = jogo["date"]
    nome_match = jogo["match_name"]
    await ctx.send(
        f"🔔 Alerta configurado para **{nome_match}** em `{data_hora}`.\n"
        "🕑 (Em 10 s você verá a notificação de demonstração)"
    )
    bot.loop.create_task(_demo_alert(ctx, nome_match))

async def _demo_alert(ctx, nome_match: str):
    await asyncio.sleep(10)
    await ctx.send(f"🚨 **DEMONSTRAÇÃO** — Começou a partida da FURIA: **{nome_match}**!")

@bot.command(name="clip")
async def clip(ctx):
    clips = [
        "https://youtu.be/furia_highlight1",
        "https://youtu.be/furia_highlight2",
        "https://youtu.be/furia_highlight3"
    ]
    await ctx.send(f"🎬 Highlight CS:GO da FURIA: {random.choice(clips)}")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latência: {bot.latency*1000:.2f} ms")

@bot.command(name="stream")
async def stream(ctx):
    info = fetch_stream_link("furia")
    if info:
        title, thumb, url = info
        embed = discord.Embed(
            title="🔴 FURIA ao vivo no Twitch!",
            description=title,
            url=url,
            color=0x9146FF
        )
        embed.set_thumbnail(url=thumb)
    else:
        embed = discord.Embed(
            title="🔴 FURIA não está ao vivo agora.",
            description="Você pode acompanhar o canal: https://twitch.tv/furia",
            color=0x9146FF
        )
    await ctx.send(embed=embed)

@bot.command(name="loja")
async def loja(ctx):
    embed = discord.Embed(
        title="🛒 Loja Oficial FURIA",
        description="Confira produtos exclusivos do time de CS:GO:",
        url=Config.SHOP_BASE_URL,
        color=0x000000
    )
    for name, link in Config.SHOP_CATEGORIES.items():
        embed.add_field(name=name, value=link, inline=True)
    embed.set_footer(text="Use o link acima ou clique nas categorias para garantir o seu!")
    await ctx.send(embed=embed)

@bot.command(name="votar")
@commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
async def votar(ctx, *, nome: str = None):
    if not nome:
        return await ctx.send("❗ Use `!votar nome_do_player`")
    await ctx.send(f"✅ Voto em **{nome}** registrado! Obrigado!")

@bot.command(name="ajuda")
async def ajuda(ctx):
    embed = discord.Embed(title="🛠️ Comandos FURIA Bot", color=0x3498DB)
    cmds = {
        "!start":      "Menu inicial",
        "!status":     "Placar ao vivo",
        "!proximos":   "Próximos jogos",
        "!resultados": "Resultados recentes",
        "!alerta":     "Alerta de início de jogo",
        "!votar <nome>":"Votar no MVP",
        "!clip":       "Highlight aleatório",
        "!ping":       "Teste de latência",
        "!stream":     "Onde assistir ao vivo",
        "!loja":       "Abrir loja oficial"
    }
    for c, d in cmds.items():
        embed.add_field(name=c, value=d, inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
