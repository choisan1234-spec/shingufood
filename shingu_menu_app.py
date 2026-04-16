import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import datetime
import urllib3
import ssl
import json
import os
import sys
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import ssl_

# Windows terminal encoding fix
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# -----------------------------------------------------------------------------
# 설정 / Configuration (기존 파일에서 유지)
# -----------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = '8287561582:AAEpMXqxwTYUusa-xqnX_mttZNgM4pT4ERU'
TELEGRAM_CHAT_ID = '8672911639'

# 신구대학교 API URL (인터넷 코드에서 가져옴)
API_URL = "https://www.shingu.ac.kr/ajaxf/FR_BST_SVC/BistroCarteInfo.do"
MENU_ID = "1630"

# 식당 정보
BISTROS = [
    {"name": "교직원식당", "seq": "6", "icon": "🏫"},
    {"name": "학생식당(미래창의관)", "seq": "5", "icon": "🎓"},
    {"name": "학생식당(서관)", "seq": "7", "icon": "🍱"}
]

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# SSL Adapter (인터넷 코드에서 가져옴)
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Main App Class
# -----------------------------------------------------------------------------
class ShinguMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏫 신구대학교 식단 알리미 (실시간)")
        self.root.geometry("600x750")
        self.root.configure(bg="#f0f4f7")

        # 1. 헤더
        header_frame = tk.Frame(root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="🍱 신구대 실시간 학식 알리미", font=("Malgun Gothic", 20, "bold"), 
                 bg="#2c3e50", fg="white").pack(pady=20)

        # 2. 버튼 영역
        btn_frame = tk.Frame(root, bg="#f0f4f7")
        btn_frame.pack(pady=20)

        self.today_btn = tk.Button(btn_frame, text="📅 오늘 식단 가져오기", font=("Malgun Gothic", 12), width=20, height=2,
                                  bg="#3498db", fg="white", activebackground="#2980b9",
                                  command=lambda: self.fetch_and_show("today"))
        self.today_btn.grid(row=0, column=0, padx=10)

        self.tomorrow_btn = tk.Button(btn_frame, text="🔜 내일 식단 가져오기", font=("Malgun Gothic", 12), width=20, height=2,
                                     bg="#e67e22", fg="white", activebackground="#d35400",
                                     command=lambda: self.fetch_and_show("tomorrow"))
        self.tomorrow_btn.grid(row=0, column=1, padx=10)

        # 3. 텍스트 박스 (스크롤 가능하게 변경)
        self.text_area = scrolledtext.ScrolledText(root, height=22, width=65, font=("Malgun Gothic", 10), 
                                                 bg="white", relief=tk.FLAT, padx=10, pady=10)
        self.text_area.pack(pady=10)

        # 4. 상태 메시지
        self.status_label = tk.Label(root, text="원하시는 날짜의 버튼을 눌러주세요.", 
                                     font=("Malgun Gothic", 10), bg="#f0f4f7", fg="#7f8c8d")
        self.status_label.pack(pady=10)

    def get_kst_now(self):
        """한국 시간(KST) 현재 시간 반환"""
        return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

    def get_menu_data(self, seq, target_date):
        """API를 통해 특정 식당의 주간 식단 데이터를 가져옴"""
        # 해당 날짜가 포함된 주간 데이터 요청
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
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

    def format_menu(self, menu_item):
        """메뉴 아이템을 보기 좋은 텍스트로 변환"""
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
                    content = content.replace('\r\n', '\n')
                    message_lines.append(content)
                message_lines.append("")
                
        if not found_any:
            return "🍽 등록된 메뉴가 없습니다."
            
        return "\n".join(message_lines).strip()

    def fetch_and_show(self, day_key):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "데이터를 불러오는 중입니다... 잠시만 기다려주세요.\n")
        self.status_label.config(text="데이터 로딩 중...", fg="#3498db")
        self.root.update()

        kst_now = self.get_kst_now()
        if day_key == "tomorrow":
            target_date = kst_now + datetime.timedelta(days=1)
        else:
            target_date = kst_now

        target_date_key = target_date.strftime("%Y%m%d")
        display_date = target_date.strftime("%Y년 %m월 %d일 (%a)")

        ui_text = f"📅 날짜: {display_date}\n"
        ui_text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        telegram_message = f"🏫 <b>신구대학교 {day_key.replace('today','오늘').replace('tomorrow','내일')}의 학식</b>\n"
        telegram_message += f"📅 {display_date}\n\n"

        success_count = 0
        for bistro in BISTROS:
            bistro_name = bistro['name']
            bistro_seq = bistro['seq']
            bistro_icon = bistro['icon']
            
            json_data = self.get_menu_data(bistro_seq, target_date)
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
                    menu_content = self.format_menu(todays_item)
                    success_count += 1
            
            ui_text += f"{bistro_icon} {bistro_name}\n{menu_content}\n"
            ui_text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            telegram_message += f"{bistro_icon} <b>{bistro_name}</b>\n{menu_content}\n\n"

        telegram_message += "맛있게 드세요! 😋"

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, ui_text)
        
        if success_count > 0:
            self.status_label.config(text="텔레그램 전송 중...", fg="#3498db")
            self.root.update()
            if self.send_to_telegram(telegram_message):
                self.status_label.config(text="✅ 전송 성공! 맛있게 드세요.", fg="#27ae60")
            else:
                self.status_label.config(text="⚠️ 데이터는 가져왔으나 텔레그램 전송 실패", fg="#e67e22")
        else:
            self.status_label.config(text="❌ 식단 데이터를 찾을 수 없습니다.", fg="#e74c3c")

    def send_to_telegram(self, text):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ShinguMenuApp(root)
    root.mainloop()
