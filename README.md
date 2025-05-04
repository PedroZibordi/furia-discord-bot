# 🤖 FURIA Tech Discord Bot

**Bot de apoio aos fãs da FURIA CS:GO**  
- Placar ao vivo  
- Próximos jogos  
- Resultados históricos  
- Highlights aleatórios  
- Streaming (Twitch)  
- Loja oficial  
- (demo) Alerta de início de partida  

## 🔧 Tecnologias

- Python 3.10+  
- `discord.py`  
- `requests`  
- `python-dotenv`  

## 🚀 Funcionalidades

| Comando           | Descrição                                               |
|-------------------|---------------------------------------------------------|
| `!start`          | Menu inicial                                            |
| `!status`         | Placar ao vivo da partida                               |
| `!proximos`       | Próximos jogos                                          |
| `!resultados`     | Resultados recentes (fallback estático)                 |
| `!alerta`         | Demonstração de alerta para próximos jogos (10 s after) |
| `!clip`           | Highlight aleatório de CS:GO                            |
| `!ping`           | Teste de latência                                       |
| `!stream`         | Onde assistir ao vivo no Twitch                         |
| `!loja`           | Link e categorias da loja oficial                       |
| `!votar <nome>`   | Votar no MVP                                            |
| `!ajuda`          | Lista de todos os comandos                              |

## ⚙️ Setup Local

1. **Clone o repositório**  
   ```bash
   git clone https://github.com/SEU_USUARIO/furia-discord-bot.git
   cd furia-discord-bot

2. **Crie um ambiente virtual**  
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

3. **Instale dependências**

pip install -r requirements.txt

4. **Configure as variáveis de ambiente**

Na raiz, crie um arquivo .env contendo:

DISCORD_TOKEN=seu_discord_bot_token
PANDASCORE_TOKEN=seu_pandascore_token
TWITCH_CLIENT_ID=seu_twitch_client_id
TWITCH_CLIENT_SECRET=seu_twitch_client_secret

5. **Execute localmente**

python main.py


No Discord, digite !start para conferir o menu inicial.