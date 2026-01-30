import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import time
import random

# =========================
# CONFIG
# =========================

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

TRADERS_TO_WATCH = [
    "0000000000000",   # xxxxxx
    "111111111111111",  # xxxxxxx

]

POLL_INTERVAL = 1  # secondes

# =========================
# DISCORD
# =========================

async def send_discord(msg):
    async with aiohttp.ClientSession() as session:
        await session.post(DISCORD_WEBHOOK, json={"content": msg})

# =========================
# POLYMARKET API
# =========================

async def fetch_trader_username(address):
    url = "https://gamma-api.polymarket.com/public-profile"
    params = {"address": address.lower()}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=12) as resp:
                if resp.status != 200:
                    print(f"Erreur profil {address}: {resp.status}")
                    return None
                data = await resp.json()
                username = (
                    data.get("username") or
                    data.get("pseudonym") or
                    data.get("name") or
                    None
                )
                return username if username else f"@{address[:6]}...{address[-4:]}"
    except Exception as e:
        print(f"Exception username {address}: {e}")
        return None

# =========================
# LISTENER VIA API
# =========================

async def listen_trader(trader):
    print(f"👀 Surveillance API /activity pour {trader}")
    last_seen_ts = int(time.time()) - 3600
    seen_hashes = set()

    while True:
        try:
            url = "https://data-api.polymarket.com/activity"
            params = {
                "user": trader.lower(),
                "limit": 20,
                "sortBy": "TIMESTAMP",
                "sortDirection": "DESC"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"Erreur {resp.status} pour {trader} - Message: {error_text}")
                        await asyncio.sleep(POLL_INTERVAL + random.uniform(0, 0.5))
                        continue

                    data = await resp.json()
                    if not isinstance(data, list) or not data:
                        await asyncio.sleep(POLL_INTERVAL + random.uniform(0, 0.5))
                        continue

                    for entry in data:
                        ts = entry.get("timestamp")
                        tx_hash = entry.get("transactionHash", "")

                        if tx_hash in seen_hashes:
                            continue
                        if ts is None or ts < last_seen_ts:
                            continue

                        act_type = entry.get("type", "").upper()
                        if act_type not in ["TRADE", "BUY", "SELL"]:
                            continue

                        usdc_amount = float(entry.get("usdcSize") or entry.get("size", 0))
                        share_amount = float(entry.get("size", 0))

                        if usdc_amount <= 0 and "price" in entry and share_amount > 0:
                            usdc_amount = share_amount * float(entry.get("price", 0))

                        if usdc_amount < 5:
                            continue

                        side = entry.get("side", "?")
                        price = entry.get("price")
                        odds_str = f"{float(price or 0):.3f}" if price else "N/A"

                        market_question = entry.get("marketQuestion", entry.get("title", "Marché inconnu"))
                        slug = entry.get("marketSlug", "").strip()
                        condition_id = entry.get("conditionId", "")
                        tx_hash = entry.get("transactionHash", "")

                        # Debug pour diagnostiquer les liens
                        print(f"DEBUG - Trade {tx_hash[:10]}...: slug='{slug}', condID='{condition_id[:10]}...', question='{market_question[:50]}...'")

                        # Lien : priorité au marché via slug
                        if slug:
                            market_url = f"https://polymarket.com/event/{slug}"  # Lien direct vers le match/pari
                        elif condition_id:
                            market_url = f"https://polymarket.com/event/{condition_id}"  # essai (parfois marche, souvent 404)
                        elif tx_hash:
                            market_url = f"https://polygonscan.com/tx/{tx_hash}"  # fallback tx (voir détails on-chain)
                        else:
                            market_url = "https://polymarket.com"

                        print(f"Trade détecté : usdcSize={usdc_amount:.2f}, size={share_amount:.0f}, price={price}, side={side}, ts={ts}")

                        username = await fetch_trader_username(trader)
                        display_name = f"{username} ({trader[:6]}...{trader[-4:]})" if username else trader

                        await notify(
                            display_name,
                            usdc_amount,
                            side,
                            odds_str,
                            market_question,
                            market_url,
                            share_amount
                        )

                        if tx_hash:
                            seen_hashes.add(tx_hash)
                        last_seen_ts = max(last_seen_ts, ts)

        except Exception as e:
            print(f"Erreur dans listen_trader API {trader}: {str(e)}")

        await asyncio.sleep(POLL_INTERVAL + random.uniform(0, 0.5))

# =========================
# NOTIFICATION
# =========================

async def notify(trader, amount_usdc, side, odds, market_name, market_url, shares=0):
    shares_str = f" ({shares:.0f} shares)" if shares > 0 else ""
    message = (
        f"🎯 **NOUVEAU TRADE POLYMARKET**\n\n"
        f"👤 Trader : **{trader}**\n"
        f"💵 Montant investi : **{amount_usdc:.2f} USDC{shares_str}**\n"
        f"📊 Direction : **{side}**\n"
        f"💰 Prix d'exécution : **{odds}**\n"
        f"📌 Marché : **{market_name}**\n"
        f"🔗 Lien marché/tx : {market_url}"
    )

    print(message)
    await send_discord(message)

# =========================
# MAIN
# =========================

async def main():
    for addr in TRADERS_TO_WATCH:
        username = await fetch_trader_username(addr)
        print(f"→ Surveillé : {username or 'Anonyme'} ({addr})")

    tasks = [asyncio.create_task(listen_trader(trader)) for trader in TRADERS_TO_WATCH]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("🚀 Polymarket Discord Trade Notifier lancé – liens prioritaires marché")
    asyncio.run(send_discord("✅ Bot lancé – liens vers marché (slug) prioritaires"))

    asyncio.run(main())
