import re
import asyncio
import httpx
import traceback
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8699109246:AAFgllLx-oTjS7sFJb_XCtcctKZhG_M3Kxg"
TARGET_GROUP_ID = "-1003393993086"
PANEL_USERNAME = "opxali"
PANEL_PASSWORD = "opxali00"
DEVELOPER_NAME = "Developer"
DEVELOPER_LINK = "https://t.me/only_possible"
CHANNEL_NAME = "Number"
CHANNEL_LINK = "https://t.me/only_possible_worlds0"

E_GLOBE = '<tg-emoji emoji-id="5467406098367521267">🌍</tg-emoji>'
E_NUM = '<tg-emoji emoji-id="5267300544094948794">📲</tg-emoji>'
E_MSG = '<tg-emoji emoji-id="5424818078833715060">💬</tg-emoji>'
E_KEY = '<tg-emoji emoji-id="5472308992514464048">🔑</tg-emoji>'

ID_COPY = "5472308992514464048"
ID_NUM = "5267300544094948794"
ID_DEV = "5453957997418004470"

global_client = None
seen_signatures = set()
is_first_run = True

async def login_to_panel():
    try:
        print("🔄 Attempting to login to panel...")
        login_headers = {
            "Host": "185.2.83.39",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,ur-PK;q=0.8,ur;q=0.7"
        }
        r1 = await global_client.get("http://185.2.83.39/ints/login", headers=login_headers)
        match = re.search(r"What is\s+(\d+)\s*([\+\-\*])\s*(\d+)\s*=\s*\?", r1.text)
        capt = "0"
        if match:
            n1, op, n2 = match.groups()
            if op == '+': capt = str(int(n1) + int(n2))
            elif op == '-': capt = str(int(n1) - int(n2))
            elif op == '*': capt = str(int(n1) * int(n2))
        
        payload = {"username": PANEL_USERNAME, "password": PANEL_PASSWORD, "capt": capt}
        post_headers = login_headers.copy()
        post_headers["Content-Type"] = "application/x-www-form-urlencoded"
        post_headers["Origin"] = "http://185.2.83.39"
        post_headers["Referer"] = "http://185.2.83.39/ints/login"
        
        await global_client.post("http://185.2.83.39/ints/signin", data=payload, headers=post_headers)
        print("✅ Panel Login Successful!")
        return True
    except Exception as e:
        print(f"❌ Panel Login Failed: {e}")
        return False

async def get_session_key():
    try:
        print("🔄 Fetching Session Key...")
        headers = {
            "Host": "185.2.83.39",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "http://185.2.83.39/ints/agent/SMSDashboard",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,ur-PK;q=0.8,ur;q=0.7"
        }
        r = await global_client.get("http://185.2.83.39/ints/agent/SMSCDRReports", headers=headers)
        match = re.search(r"sesskey=([A-Za-z0-9=]+)", r.text)
        if match:
            sesskey = match.group(1)
            print(f"🔑 Session Key Found: {sesskey}")
            return sesskey
        print("⚠️ Session Key Not Found!")
        return ""
    except Exception as e:
        print(f"❌ Error Getting Session Key: {e}")
        return ""

def normalize_record(rec):
    try:
        if isinstance(rec, list) and len(rec) >= 6:
            if "0.2,0,0,0" in str(rec[0]) or str(rec[0]).startswith("0,0"):
                return None
            return {
                "Date-and-time": str(rec[0]),
                "Service": str(rec[3]),
                "Number": str(rec[2]),
                "Full_message": str(rec[5]) if rec[5] else str(rec[4])
            }
    except Exception:
        pass
    return None

async def send_vip_card(chat_id, raw_record, is_test=False):
    record = normalize_record(raw_record)
    if not record: return
    
    service = record.get("Service", "Unknown")
    number = record.get("Number", "N/A")
    raw_msg = record.get("Full_message", "")
    
    otp_match = re.search(r'\d{3}[-\s]?\d{3}|\d{4,6}', raw_msg)
    otp = otp_match.group(0) if otp_match else "N/A"

    test_badge = "🟢 <b>[TEST MESSAGE]</b>\n" if is_test else ""

    text = (
        f"{test_badge}"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_GLOBE} <b>New {service} OTP Arrived!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_NUM} <b>Number:</b> <code>+{number}</code>\n"
        f"{E_KEY} <b>OTP Code:</b> <code>{otp}</code>\n\n"
        f"{E_MSG} <b>Message:</b>\n<pre>{raw_msg}</pre>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": f"Copy: {otp}",
                    "copy_text": {"text": otp},
                    "icon_custom_emoji_id": ID_COPY,
                    "style": "success"
                }
            ],
            [
                {
                    "text": CHANNEL_NAME,
                    "url": CHANNEL_LINK,
                    "icon_custom_emoji_id": ID_NUM,
                    "style": "danger"
                },
                {
                    "text": DEVELOPER_NAME,
                    "url": DEVELOPER_LINK,
                    "icon_custom_emoji_id": ID_DEV,
                    "style": "primary"
                }
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    }

    try:
        print(f"📤 Sending message to group {chat_id}...")
        r = await global_client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
        if r.status_code == 200:
            print("✅ Message Sent to Group Successfully!")
        else:
            print(f"❌ Telegram API Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Telegram Send Exception: {e}")

async def background_otp_fetcher(app: Application):
    global is_first_run, global_client
    print("🚀 Background fetcher task started!")
    global_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    
    await login_to_panel()
    sesskey = await get_session_key()

    while True:
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            headers = {
                "Host": "185.2.83.39",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://185.2.83.39/ints/agent/SMSCDRReports",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9,ur-PK;q=0.8,ur;q=0.7"
            }

            url = f"http://185.2.83.39/ints/agent/res/data_smscdr.php?fdate1={today}%2000:00:00&fdate2={today}%2023:59:59&frange=&fclient=&fnum=&fcli=&fgdate=&fgmonth=&fgrange=&fgclient=&fgnumber=&fgcli=&fg=0&sesskey={sesskey}&sEcho=1&iColumns=9&sColumns=%2C%2C%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=25&mDataProp_0=0&sSearch_0=&bRegex_0=false&bSearchable_0=true&bSortable_0=true&mDataProp_1=1&sSearch_1=&bRegex_1=false&bSearchable_1=true&bSortable_1=true&mDataProp_2=2&sSearch_2=&bRegex_2=false&bSearchable_2=true&bSortable_2=true&mDataProp_3=3&sSearch_3=&bRegex_3=false&bSearchable_3=true&bSortable_3=true&mDataProp_4=4&sSearch_4=&bRegex_4=false&bSearchable_4=true&bSortable_4=true&mDataProp_5=5&sSearch_5=&bRegex_5=false&bSearchable_5=true&bSortable_5=true&mDataProp_6=6&sSearch_6=&bRegex_6=false&bSearchable_6=true&bSortable_6=true&mDataProp_7=7&sSearch_7=&bRegex_7=false&bSearchable_7=true&bSortable_7=true&mDataProp_8=8&sSearch_8=&bRegex_8=false&bSearchable_8=true&bSortable_8=false&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1&_=1774500971502"
            
            print(f"📡 Hitting API endpoint... (Session: {sesskey})")
            r = await global_client.get(url, headers=headers)
            
            try:
                data = r.json()
                print("✅ API Responded with JSON Data!")
            except Exception:
                print("🔄 API response invalid/Session Expired! Re-login initiating...")
                await login_to_panel()
                sesskey = await get_session_key()
                if sesskey:
                    url = url.replace(re.search(r"sesskey=([A-Za-z0-9=]*)", url).group(1), sesskey)
                r = await global_client.get(url, headers=headers)
                try:
                    data = r.json()
                    print("✅ API Responded with JSON Data after Re-login!")
                except Exception as e:
                    print(f"❌ Failed again after re-login: {e}")
                    await asyncio.sleep(5)
                    continue

            records = data.get("aaData", [])
            if not isinstance(records, list):
                print("⚠️ 'aaData' is not a list! Skipping...")
                await asyncio.sleep(5)
                continue

            print(f"📊 Found {len(records)} records from API.")

            if is_first_run:
                print("🚀 First run detected. Processing first OTP as test...")
                if records:
                    for rec in records:
                        norm = normalize_record(rec)
                        if norm:
                            await send_vip_card(TARGET_GROUP_ID, norm, is_test=True)
                            break
                
                for rec in records:
                    norm = normalize_record(rec)
                    if norm:
                        sig = f"{norm['Date-and-time']}|{norm['Number']}"
                        seen_signatures.add(sig)
                
                is_first_run = False
                print("✅ First run complete. Waiting for new OTPs in background...")
                await asyncio.sleep(5)
                continue

            new_count = 0
            for rec in reversed(records):
                norm = normalize_record(rec)
                if not norm: continue
                sig = f"{norm['Date-and-time']}|{norm['Number']}"
                
                if sig not in seen_signatures:
                    print(f"✨ New OTP Found: {norm['Number']}")
                    await send_vip_card(TARGET_GROUP_ID, norm)
                    seen_signatures.add(sig)
                    new_count += 1
            
            if new_count > 0:
                print(f"✅ Processed {new_count} new OTPs.")

            if len(seen_signatures) > 5000:
                seen_signatures.clear()

        except Exception as e:
            print(f"⚠️ Fetcher Loop Error: {e}")
            traceback.print_exc()
        
        await asyncio.sleep(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 Start command received!")
    welcome_msg = (
        f"🌟 <b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗩𝗜𝗣 𝗢𝗧𝗣 𝗕𝗢𝗧</b> 🌟\n\n"
        f"👑 <b>Status:</b> <code>System is Active & Running!</code>\n"
        f"⚡ <b>Speed:</b> <code>Ultra Fast Fetching</code>\n"
        f"🛡️ <b>Security:</b> <code>Bypass Enabled</code>\n\n"
        f"💎 <i>Get ready for premium uninterrupted OTPs directly here!</i>"
    )
    await update.message.reply_html(welcome_msg)

async def on_startup(app: Application):
    print("⚙️ Running startup routines...")
    asyncio.create_task(background_otp_fetcher(app))

def main():
    print("🤖 Bot is starting up...")
    app = Application.builder().token(BOT_TOKEN).post_init(on_startup).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
