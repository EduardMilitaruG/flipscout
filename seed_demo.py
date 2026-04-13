"""
seed_demo.py — Populate flipscout.db with realistic demo data.
Run once: python seed_demo.py
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

DB_PATH = Path(__file__).parent / "flipscout.db"

# ── Helpers ────────────────────────────────────────────────────────────────────

def ts(hours_ago=0, minutes_ago=0):
    t = datetime.utcnow() - timedelta(hours=hours_ago, minutes=minutes_ago)
    return t.isoformat()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

# ── Listings + Deals ───────────────────────────────────────────────────────────

DEALS = [
    # ── TECH ──────────────────────────────────────────────────────────────────
    {
        "title": "Sony PlayStation 5 Slim Digital Edition ほぼ新品",
        "price_jpy": 32000, "price_usd": 213,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456001",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=PS5",
        "keyword": "PS5 slim", "category": "tech", "marketplace": "zenmarket",
        "condition": "like_new",
        "jp_price_eur": 198, "shipping_eur": 28, "platform_fee_eur": 26,
        "spanish_resale_eur": 340, "comparable_count": 14,
        "gross_margin_eur": 88, "margin_pct": 25.9,
        "is_risky": 0, "confidence": "high", "hours_ago": 1,
    },
    {
        "title": "Nintendo Switch OLED ホワイト 美品 箱付き",
        "price_jpy": 18500, "price_usd": 123,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456002",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=NSW",
        "keyword": "Switch OLED", "category": "tech", "marketplace": "zenmarket",
        "condition": "good",
        "jp_price_eur": 115, "shipping_eur": 22, "platform_fee_eur": 18,
        "spanish_resale_eur": 240, "comparable_count": 22,
        "gross_margin_eur": 85, "margin_pct": 35.4,
        "is_risky": 0, "confidence": "high", "hours_ago": 2,
    },
    {
        "title": "Sony WH-1000XM5 ワイヤレスヘッドフォン ブラック",
        "price_jpy": 14000, "price_usd": 93,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456003",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=XM5",
        "keyword": "WH-1000XM5", "category": "tech", "marketplace": "zenmarket",
        "condition": "good",
        "jp_price_eur": 87, "shipping_eur": 18, "platform_fee_eur": 15,
        "spanish_resale_eur": 200, "comparable_count": 31,
        "gross_margin_eur": 80, "margin_pct": 40.0,
        "is_risky": 0, "confidence": "high", "hours_ago": 3,
    },
    {
        "title": "Apple AirPods Pro 第2世代 MagSafe対応 未使用",
        "price_jpy": 12000, "price_usd": 80,
        "url": "https://jp.mercari.com/item/m123456004",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=APs",
        "keyword": "AirPods Pro 2", "category": "tech", "marketplace": "mercari_jp",
        "condition": "like_new",
        "jp_price_eur": 74, "shipping_eur": 14, "platform_fee_eur": 13,
        "spanish_resale_eur": 170, "comparable_count": 28,
        "gross_margin_eur": 69, "margin_pct": 40.6,
        "is_risky": 0, "confidence": "high", "hours_ago": 4,
    },
    {
        "title": "Fujifilm X100VI シルバー 新品同様 付属品完備",
        "price_jpy": 145000, "price_usd": 967,
        "url": "https://jp.mercari.com/item/m123456005",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=X100",
        "keyword": "Fujifilm X100VI", "category": "tech", "marketplace": "mercari_jp",
        "condition": "like_new",
        "jp_price_eur": 898, "shipping_eur": 42, "platform_fee_eur": 75,
        "spanish_resale_eur": 1380, "comparable_count": 9,
        "gross_margin_eur": 365, "margin_pct": 26.4,
        "is_risky": 0, "confidence": "medium", "hours_ago": 5,
    },
    {
        "title": "Steam Deck 512GB LCD 美品 ケース付き",
        "price_jpy": 38000, "price_usd": 253,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456006",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=SD",
        "keyword": "Steam Deck", "category": "tech", "marketplace": "zenmarket",
        "condition": "good",
        "jp_price_eur": 235, "shipping_eur": 32, "platform_fee_eur": 24,
        "spanish_resale_eur": 390, "comparable_count": 11,
        "gross_margin_eur": 99, "margin_pct": 25.4,
        "is_risky": 0, "confidence": "medium", "hours_ago": 6,
    },
    {
        "title": "ASUS ROG Ally Z1 Extreme ゲーミングPC 動作確認済",
        "price_jpy": 52000, "price_usd": 347,
        "url": "https://jp.mercari.com/item/m123456007",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=ROG",
        "keyword": "ROG Ally", "category": "tech", "marketplace": "mercari_jp",
        "condition": "good",
        "jp_price_eur": 322, "shipping_eur": 36, "platform_fee_eur": 28,
        "spanish_resale_eur": 520, "comparable_count": 7,
        "gross_margin_eur": 134, "margin_pct": 25.8,
        "is_risky": 0, "confidence": "medium", "hours_ago": 7,
    },
    {
        "title": "Sony α7C II ボディ シルバー 美品",
        "price_jpy": 195000, "price_usd": 1300,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456008",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=a7C",
        "keyword": "Sony A7C II", "category": "tech", "marketplace": "zenmarket",
        "condition": "like_new",
        "jp_price_eur": 1208, "shipping_eur": 48, "platform_fee_eur": 98,
        "spanish_resale_eur": 1750, "comparable_count": 6,
        "gross_margin_eur": 396, "margin_pct": 22.6,
        "is_risky": 0, "confidence": "medium", "hours_ago": 9,
    },
    {
        "title": "Meta Quest 3 128GB スタンドアローン VR",
        "price_jpy": 42000, "price_usd": 280,
        "url": "https://jp.mercari.com/item/m123456009",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=MQ3",
        "keyword": "Meta Quest 3", "category": "tech", "marketplace": "mercari_jp",
        "condition": "good",
        "jp_price_eur": 260, "shipping_eur": 30, "platform_fee_eur": 22,
        "spanish_resale_eur": 410, "comparable_count": 13,
        "gross_margin_eur": 98, "margin_pct": 23.9,
        "is_risky": 0, "confidence": "medium", "hours_ago": 10,
    },
    {
        "title": "Anker Portable Power Station 注目品 PowerHouse",
        "price_jpy": 8500, "price_usd": 57,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456010",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=ANK",
        "keyword": "Anker PowerHouse", "category": "tech", "marketplace": "zenmarket",
        "condition": "good",
        "jp_price_eur": 53, "shipping_eur": 24, "platform_fee_eur": 9,
        "spanish_resale_eur": 120, "comparable_count": 4,
        "gross_margin_eur": 34, "margin_pct": 28.3,
        "is_risky": 0, "confidence": "low", "hours_ago": 12,
    },

    # ── POKEMON ───────────────────────────────────────────────────────────────
    {
        "title": "PSA10 リザードン VMAX SA 068/190 シャイニースターV",
        "price_jpy": 22000, "price_usd": 147,
        "url": "https://jp.mercari.com/item/m123456011",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=PSA",
        "keyword": "Charizard VMAX SA PSA10", "category": "pokemon", "marketplace": "mercari_jp",
        "condition": "PSA10",
        "jp_price_eur": 136, "shipping_eur": 8, "platform_fee_eur": 18,
        "spanish_resale_eur": 280, "comparable_count": 19,
        "gross_margin_eur": 118, "margin_pct": 42.1,
        "is_risky": 0, "confidence": "high", "hours_ago": 2,
    },
    {
        "title": "PSA10 ピカチュウ V-UNION 特別版 未使用",
        "price_jpy": 8500, "price_usd": 57,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456012",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=PKU",
        "keyword": "Pikachu V-UNION PSA10", "category": "pokemon", "marketplace": "zenmarket",
        "condition": "PSA10",
        "jp_price_eur": 53, "shipping_eur": 8, "platform_fee_eur": 9,
        "spanish_resale_eur": 105, "comparable_count": 12,
        "gross_margin_eur": 35, "margin_pct": 33.3,
        "is_risky": 0, "confidence": "high", "hours_ago": 3,
    },
    {
        "title": "PSA9 ミュウツー GX HR 068/060 スーパーバースト",
        "price_jpy": 4200, "price_usd": 28,
        "url": "https://jp.mercari.com/item/m123456013",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=MTW",
        "keyword": "Mewtwo GX HR PSA9", "category": "pokemon", "marketplace": "mercari_jp",
        "condition": "PSA9",
        "jp_price_eur": 26, "shipping_eur": 8, "platform_fee_eur": 5,
        "spanish_resale_eur": 65, "comparable_count": 16,
        "gross_margin_eur": 26, "margin_pct": 40.0,
        "is_risky": 0, "confidence": "high", "hours_ago": 5,
    },
    {
        "title": "PSA10 イーブイズ ヒーローズ まとめ 5枚セット HR",
        "price_jpy": 15000, "price_usd": 100,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456014",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=EVE",
        "keyword": "Eevee Heroes HR PSA10", "category": "pokemon", "marketplace": "zenmarket",
        "condition": "PSA10",
        "jp_price_eur": 93, "shipping_eur": 10, "platform_fee_eur": 13,
        "spanish_resale_eur": 195, "comparable_count": 8,
        "gross_margin_eur": 79, "margin_pct": 40.5,
        "is_risky": 0, "confidence": "medium", "hours_ago": 8,
    },
    {
        "title": "PSA10 ゲンガー VMAX SA 282/184 マッチ対戦",
        "price_jpy": 6800, "price_usd": 45,
        "url": "https://jp.mercari.com/item/m123456015",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=GNG",
        "keyword": "Gengar VMAX SA PSA10", "category": "pokemon", "marketplace": "mercari_jp",
        "condition": "PSA10",
        "jp_price_eur": 42, "shipping_eur": 8, "platform_fee_eur": 7,
        "spanish_resale_eur": 90, "comparable_count": 11,
        "gross_margin_eur": 33, "margin_pct": 36.7,
        "is_risky": 0, "confidence": "high", "hours_ago": 11,
    },

    # ── FASHION ───────────────────────────────────────────────────────────────
    {
        "title": "Supreme Box Logo Hoodie FW23 Black L 新品未使用",
        "price_jpy": 28000, "price_usd": 187,
        "url": "https://jp.mercari.com/item/m123456016",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=SUP",
        "keyword": "Supreme Box Logo Hoodie", "category": "fashion", "marketplace": "mercari_jp",
        "condition": "new",
        "jp_price_eur": 173, "shipping_eur": 16, "platform_fee_eur": 22,
        "spanish_resale_eur": 340, "comparable_count": 17,
        "gross_margin_eur": 129, "margin_pct": 37.9,
        "is_risky": 0, "confidence": "high", "hours_ago": 2,
    },
    {
        "title": "Stone Island Shadow Project Jacket M 日本限定",
        "price_jpy": 45000, "price_usd": 300,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456017",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=SI",
        "keyword": "Stone Island Shadow Project", "category": "fashion", "marketplace": "zenmarket",
        "condition": "good",
        "jp_price_eur": 279, "shipping_eur": 20, "platform_fee_eur": 30,
        "spanish_resale_eur": 520, "comparable_count": 6,
        "gross_margin_eur": 191, "margin_pct": 36.7,
        "is_risky": 0, "confidence": "medium", "hours_ago": 4,
    },
    {
        "title": "Nike Air Jordan 1 High OG Chicago 2022 27cm DS",
        "price_jpy": 38000, "price_usd": 253,
        "url": "https://jp.mercari.com/item/m123456018",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=AJ1",
        "keyword": "Jordan 1 Chicago", "category": "fashion", "marketplace": "mercari_jp",
        "condition": "new",
        "jp_price_eur": 235, "shipping_eur": 18, "platform_fee_eur": 26,
        "spanish_resale_eur": 420, "comparable_count": 24,
        "gross_margin_eur": 141, "margin_pct": 33.6,
        "is_risky": 0, "confidence": "high", "hours_ago": 6,
    },
    {
        "title": "Comme des Garçons PLAY Heart Tee White XL CDG",
        "price_jpy": 7500, "price_usd": 50,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456019",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=CDG",
        "keyword": "CDG PLAY tee", "category": "fashion", "marketplace": "zenmarket",
        "condition": "like_new",
        "jp_price_eur": 46, "shipping_eur": 14, "platform_fee_eur": 8,
        "spanish_resale_eur": 110, "comparable_count": 13,
        "gross_margin_eur": 42, "margin_pct": 38.2,
        "is_risky": 0, "confidence": "high", "hours_ago": 7,
    },
    {
        "title": "Yohji Yamamoto Y's ウールコート 2023 黒 Size 2",
        "price_jpy": 32000, "price_usd": 213,
        "url": "https://jp.mercari.com/item/m123456020",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=YY",
        "keyword": "Yohji Yamamoto coat", "category": "fashion", "marketplace": "mercari_jp",
        "condition": "good",
        "jp_price_eur": 198, "shipping_eur": 22, "platform_fee_eur": 24,
        "spanish_resale_eur": 390, "comparable_count": 5,
        "gross_margin_eur": 146, "margin_pct": 37.4,
        "is_risky": 0, "confidence": "medium", "hours_ago": 10,
    },
    {
        "title": "Adidas Yeezy Boost 350 V2 Zebra 28cm 新品",
        "price_jpy": 24000, "price_usd": 160,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456021",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=YZY",
        "keyword": "Yeezy 350 Zebra", "category": "fashion", "marketplace": "zenmarket",
        "condition": "new",
        "jp_price_eur": 149, "shipping_eur": 16, "platform_fee_eur": 16,
        "spanish_resale_eur": 260, "comparable_count": 20,
        "gross_margin_eur": 79, "margin_pct": 30.4,
        "is_risky": 0, "confidence": "high", "hours_ago": 14,
    },
    {
        "title": "Issey Miyake Pleats Please ロングスカート S サイズ",
        "price_jpy": 9800, "price_usd": 65,
        "url": "https://jp.mercari.com/item/m123456022",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=IM",
        "keyword": "Issey Miyake pleats", "category": "fashion", "marketplace": "mercari_jp",
        "condition": "good",
        "jp_price_eur": 61, "shipping_eur": 14, "platform_fee_eur": 9,
        "spanish_resale_eur": 135, "comparable_count": 8,
        "gross_margin_eur": 51, "margin_pct": 37.8,
        "is_risky": 0, "confidence": "medium", "hours_ago": 16,
    },

    # ── GENERAL ───────────────────────────────────────────────────────────────
    {
        "title": "Hasselblad XCD 65mm f/2.8 レンズ 中判カメラ用",
        "price_jpy": 185000, "price_usd": 1233,
        "url": "https://zenmarket.jp/auction.aspx?itemCode=z123456023",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=HBL",
        "keyword": "Hasselblad XCD 65", "category": "general", "marketplace": "zenmarket",
        "condition": "good",
        "jp_price_eur": 1146, "shipping_eur": 40, "platform_fee_eur": 90,
        "spanish_resale_eur": 1800, "comparable_count": 3,
        "gross_margin_eur": 524, "margin_pct": 29.1,
        "is_risky": 1, "confidence": "low", "hours_ago": 18,
    },
    {
        "title": "Leica Q2 Monochrom デジタルカメラ 美品 付属完備",
        "price_jpy": 420000, "price_usd": 2800,
        "url": "https://jp.mercari.com/item/m123456024",
        "thumbnail": "https://placehold.co/80x80/1a1a1a/555?text=LCA",
        "keyword": "Leica Q2 Monochrom", "category": "general", "marketplace": "mercari_jp",
        "condition": "like_new",
        "jp_price_eur": 2601, "shipping_eur": 55, "platform_fee_eur": 190,
        "spanish_resale_eur": 4100, "comparable_count": 4,
        "gross_margin_eur": 1254, "margin_pct": 30.6,
        "is_risky": 1, "confidence": "low", "hours_ago": 20,
    },
]

# ── Snipe targets ──────────────────────────────────────────────────────────────

TARGETS = [
    {
        "id": "snipe_ps5",
        "query": "PS5 slim",
        "category": "tech",
        "platform": json.dumps(["wallapop", "vinted"]),
        "max_buy_price_eur": 350,
        "min_margin_pct": 20,
        "auto_buy": 0,
        "reserve_on_match": 1,
        "active": 1,
    },
    {
        "id": "snipe_charizard",
        "query": "PSA 10 Charizard",
        "category": "pokemon",
        "platform": json.dumps(["wallapop"]),
        "max_buy_price_eur": 150,
        "min_margin_pct": 25,
        "auto_buy": 0,
        "reserve_on_match": 1,
        "active": 1,
    },
    {
        "id": "snipe_supreme",
        "query": "Supreme Box Logo",
        "category": "fashion",
        "platform": json.dumps(["vinted", "wallapop"]),
        "max_buy_price_eur": 200,
        "min_margin_pct": 30,
        "auto_buy": 0,
        "reserve_on_match": 1,
        "active": 0,
    },
    {
        "id": "snipe_airpods",
        "query": "AirPods Pro 2",
        "category": "tech",
        "platform": json.dumps(["wallapop"]),
        "max_buy_price_eur": 120,
        "min_margin_pct": 20,
        "auto_buy": 0,
        "reserve_on_match": 1,
        "active": 1,
    },
]

# ── Snipe events ───────────────────────────────────────────────────────────────

EVENTS = [
    {
        "target_id": "snipe_ps5",
        "listing_url": "https://es.wallapop.com/item/ps5-slim-digital-123001",
        "listing_title": "PlayStation 5 Slim Digital - como nueva, caja original",
        "platform": "wallapop",
        "listing_price_eur": 290,
        "calc_margin_pct": 14.7,
        "action": "skipped",
        "notes": "Margin below threshold (14.7% < 20%)",
        "minutes_ago": 8,
    },
    {
        "target_id": "snipe_ps5",
        "listing_url": "https://es.wallapop.com/item/ps5-slim-bundle-123002",
        "listing_title": "PS5 Slim + 2 mandos + 3 juegos - negociable",
        "platform": "wallapop",
        "listing_price_eur": 310,
        "calc_margin_pct": 8.5,
        "action": "skipped",
        "notes": "Margin below threshold",
        "minutes_ago": 24,
    },
    {
        "target_id": "snipe_charizard",
        "listing_url": "https://es.wallapop.com/item/charizard-psa10-123003",
        "listing_title": "Charizard Holo Base Set PSA 10 - gem mint",
        "platform": "wallapop",
        "listing_price_eur": 95,
        "calc_margin_pct": 38.2,
        "action": "messaged",
        "notes": "Sent offer message to seller",
        "minutes_ago": 45,
    },
    {
        "target_id": "snipe_airpods",
        "listing_url": "https://www.vinted.es/items/airpods-pro-2-123004",
        "listing_title": "AirPods Pro 2da generación - perfecto estado con estuche",
        "platform": "vinted",
        "listing_price_eur": 98,
        "calc_margin_pct": 27.4,
        "action": "messaged",
        "notes": "Reserved item, awaiting seller response",
        "minutes_ago": 90,
    },
    {
        "target_id": "snipe_ps5",
        "listing_url": "https://es.wallapop.com/item/ps5-slim-disc-123005",
        "listing_title": "PlayStation 5 Slim edición disco - factura incluida",
        "platform": "wallapop",
        "listing_price_eur": 340,
        "calc_margin_pct": None,
        "action": "skipped",
        "notes": "Disc edition, wrong variant",
        "minutes_ago": 130,
    },
    {
        "target_id": "snipe_charizard",
        "listing_url": "https://es.wallapop.com/item/charizard-graded-123006",
        "listing_title": "Charizard PSA 9 - carta graduada certificada",
        "platform": "wallapop",
        "listing_price_eur": 55,
        "calc_margin_pct": 11.0,
        "action": "skipped",
        "notes": "PSA 9 not PSA 10, wrong grade",
        "minutes_ago": 180,
    },
    {
        "target_id": "snipe_airpods",
        "listing_url": "https://es.wallapop.com/item/airpods-pro-fake-123007",
        "listing_title": "AirPods Pro 2 - precio negociable envío incluido",
        "platform": "wallapop",
        "listing_price_eur": 45,
        "calc_margin_pct": None,
        "action": "skipped",
        "notes": "Price too low — likely counterfeit",
        "minutes_ago": 220,
    },
    {
        "target_id": "snipe_charizard",
        "listing_url": "https://www.vinted.es/items/charizard-psa10-vmax-123008",
        "listing_title": "Charizard VMAX SA PSA 10 - Shiny Star V",
        "platform": "vinted",
        "listing_price_eur": 130,
        "calc_margin_pct": 46.1,
        "action": "messaged",
        "notes": "High-confidence match — messaged seller immediately",
        "minutes_ago": 300,
    },
]

# ── Insert ─────────────────────────────────────────────────────────────────────

def run():
    conn = get_conn()

    # Wipe existing demo data
    conn.execute("DELETE FROM snipe_events")
    conn.execute("DELETE FROM deals")
    conn.execute("DELETE FROM listings")
    conn.execute("DELETE FROM snipe_targets")

    now = ts()

    for d in DEALS:
        hours = d.pop("hours_ago")
        seen = ts(hours_ago=hours)

        conn.execute("""
            INSERT OR REPLACE INTO listings
              (title, price_jpy, price_usd, url, thumbnail, keyword, category, marketplace, condition, seen_at, alerted)
            VALUES (?,?,?,?,?,?,?,?,?,?,1)
        """, (d["title"], d["price_jpy"], d["price_usd"], d["url"], d["thumbnail"],
              d["keyword"], d["category"], d["marketplace"], d["condition"], seen))

        conn.execute("""
            INSERT INTO deals
              (listing_url, jp_price_eur, shipping_eur, platform_fee_eur,
               spanish_resale_eur, comparable_count, gross_margin_eur,
               margin_pct, is_risky, confidence, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (d["url"], d["jp_price_eur"], d["shipping_eur"], d["platform_fee_eur"],
              d["spanish_resale_eur"], d["comparable_count"], d["gross_margin_eur"],
              d["margin_pct"], d["is_risky"], d["confidence"], seen))

    for t in TARGETS:
        conn.execute("""
            INSERT OR REPLACE INTO snipe_targets
              (id, query, category, platform, max_buy_price_eur, min_margin_pct,
               auto_buy, reserve_on_match, active, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (t["id"], t["query"], t["category"], t["platform"],
              t["max_buy_price_eur"], t["min_margin_pct"],
              t["auto_buy"], t["reserve_on_match"], t["active"], now, now))

    for e in EVENTS:
        minutes = e.pop("minutes_ago")
        occurred = ts(minutes_ago=minutes)
        conn.execute("""
            INSERT INTO snipe_events
              (target_id, listing_url, listing_title, platform, listing_price_eur,
               calc_margin_pct, action, notes, occurred_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (e["target_id"], e["listing_url"], e["listing_title"], e["platform"],
              e["listing_price_eur"], e["calc_margin_pct"], e["action"], e["notes"], occurred))

    conn.commit()
    conn.close()

    print(f"✓ Seeded {len(DEALS)} deals, {len(TARGETS)} targets, {len(EVENTS)} events")

if __name__ == "__main__":
    run()
