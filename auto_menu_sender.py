import requests
import datetime
import urllib3
import ssl
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_

# GitHub Secrets에서 가져올 값들 (만약 없다면 유저가 제공한 값을 기본으로 사용)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8715208527:AAEKfojeK3-7XlsvwdY_OQryPb-QLdPnVp8')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '8763086545')

API_URL = "https://www.shingu.ac.kr/ajaxf/FR_BST_SVC/BistroCarteInfo.do"
MENU_ID = "1630"
BISTROS = [
    {"name": "교직원식당", "seq": "6", "icon": "🏫"},
    {"name": "학생식당(미래창의관)", "seq": "5", "icon": "🎓"},
    {"name": "학생식당(서관)", "seq": "7", "icon": "🍱"}
]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl_.create_urllib3_context(ciphers='DEFAULT:@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

def get_kst_now():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

def get_menu_data(seq, target_date):
    monday = target_date - datetime.timedelta(days=target_date.weekday())
    friday = monday + datetime.timedelta(days=6)
    
    start_day_str = monday.strftime("%Y.%m.%d")
    end_day_str = friday.strftime("%Y.%m.%d")
    
    payload = {
        'MENU_ID': MENU_ID,
        'BISTRO_SEQ': seq,
        'START_DAY': start_day_str,
        'END_DAY': end_day_str
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    session = requests.Session()
    session.mount('https://', LegacySSLAdapter())
    
    try:
        response = session.post(API_URL, data=payload, headers=headers, verify=False, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[{seq}] API 호출 실패: {e}")
        return None

def format_menu(menu_item):
    message_lines = []
    found_any = False
    for i in range(1, 7):
        nm_key = f'CARTE{i}_NM'
        cont_key = f'CARTE{i}_CONT'
        
        title = (menu_item.get(nm_key) or '').strip()
        content = (menu_item.get(cont_key) or '').strip()
        
        if title or content:
            found_any = True
            if title:
                message_lines.append(f"🔸 {title}")
            if content:
                message_lines.append(content.replace('\r\n', '\n'))
            message_lines.append("")
            
    if not found_any:
        return "🍽 등록된 메뉴가 없습니다."
    return "\n".join(message_lines).strip()

def send_to_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("토큰 또는 Chat ID가 설정되지 않았습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("ok", False)
    except Exception as e:
        print(f"텔레그램 전송 오류: {e}")
        return False

def main():
    target_date = get_kst_now()
    target_date_key = target_date.strftime("%Y%m%d")
    display_date = target_date.strftime("%Y년 %m월 %d일 (%a)")
    
    telegram_message = f"🏫 <b>신구대학교 오늘의 학식</b>\n📅 {display_date}\n\n"
    success_count = 0
    
    for bistro in BISTROS:
        bistro_name = bistro['name']
        bistro_seq = bistro['seq']
        bistro_icon = bistro['icon']
        
        json_data = get_menu_data(bistro_seq, target_date)
        menu_content = "❌ 식단 데이터가 없습니다."
        
        if json_data:
            items = []
            if isinstance(json_data, dict) and 'data' in json_data:
                items = json_data['data']
            elif isinstance(json_data, list):
                items = json_data
            
            todays_item = None
            for item in items:
                item_date = item.get('STD_DT')
                if not item_date:
                    ym = item.get('STD_YM', '').replace('.', '')
                    dd = item.get('STD_DD', '')
                    if ym and dd:
                        item_date = f"{ym}{dd}"
                if item_date == target_date_key:
                    todays_item = item
                    break
            
            if todays_item:
                menu_content = format_menu(todays_item)
                success_count += 1
        
        telegram_message += f"{bistro_icon} <b>{bistro_name}</b>\n{menu_content}\n\n"

    telegram_message += "맛있게 드세요! 😋"
    
    print("텔레그램으로 식단 정보를 전송합니다...")
    if success_count > 0:
        if send_to_telegram(telegram_message):
            print("전송 성공!")
        else:
            print("전송 실패!")
    else:
        print("식단 데이터가 없어서 전송하지 않습니다.")

if __name__ == '__main__':
    main()
