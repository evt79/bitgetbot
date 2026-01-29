import requests
import os

# Configuración
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_data():
    url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=USDT-FUTURES"
    response = requests.get(url).json()
    return response.get('data', [])

def run_bot():
    data = get_data()
    clusters = {
        'IA': ['FET', 'AGIX', 'RNDR', 'AI', 'WLD', 'ARKM', 'TAO', 'NEAR', 'GRT', 'AKT'],
        'MEMES': ['PEPE', 'DOGE', 'SHIB', 'BONK', 'FLOKI', 'WIF', 'MEME', 'ORDI', '1000SATS'],
        'L1/L2': ['SOL', 'ARB', 'OP', 'MATIC', 'AVAX', 'DOT', 'ADA', 'TIA', 'ETH'],
        'DEFI': ['UNI', 'AAVE', 'PENDLE', 'ENA', 'JUP', 'DYDX']
    }

    valid_assets = []
    for item in data:
        symbol = item['symbol'].replace('USDT', '')
        # Lógica de porcentaje que ya nos funcionó
        change = float(item.get('priceChangePercent', 0)) * 100
        vol = float(item.get('quoteVolume', 0))
        
        if vol > 1000000 and item['symbol'].endswith('USDT'):
            valid_assets.append({'symbol': symbol, 'change': change})

    if not valid_assets:
        return

    sorted_assets = sorted(valid_assets, key=lambda x: x['change'], reverse=True)
    leader = sorted_assets[0]
    
    # Determinar sector
    sector = "Mercado General"
    sympathy = []
    for name, symbols in clusters.items():
        if leader['symbol'] in symbols:
            sector = name
            sympathy = [a for a in sorted_assets if a['symbol'] in symbols and a['symbol'] != leader['symbol']]
            break
    
    if not sympathy:
        sympathy = sorted_assets[1:4]

    # Formatear Mensaje
    msg = f"🚨 *BITGET FUTUROS: ALERTA NARRATIVA* 🚨\n\n"
    msg += f"🥇 *Líder Actual:* {leader['symbol']} (+{leader['change']:.2f}%)\n"
    msg += f"🌐 *Sector:* {sector}\n"
    msg += f"📈 [Analizar {leader['symbol']} en TV](https://www.tradingview.com/chart/?symbol=BITGET:{leader['symbol']}USDT.P)\n\n"
    msg += f"🧬 *Sympathy Plays:*\n"
    
    for p in sympathy[:3]:
        msg += f"• {p['symbol']} (+{p['change']:.2f}%) ➔ [Ver Gráfico](https://www.tradingview.com/chart/?symbol=BITGET:{p['symbol']}USDT.P)\n"
    
    msg += f"\n✅ _Solo activos con Futuros y Liquidez_"

    # Enviar a Telegram
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(send_url, data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown', 'disable_web_page_preview': 'true'})

if __name__ == "__main__":
    run_bot()