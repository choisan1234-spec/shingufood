import urllib.request
import json
from datetime import datetime

# -----------------------------------------------------------------------------
# 설정 / Configuration
# -----------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = '8287561582:AAEpMXqxwTYUusa-xqnX_mttZNgM4pT4ERU'
TELEGRAM_CHAT_ID = '8672911639'

def get_today_menu():
    """스크래핑한 오늘자 식단 데이터를 반환합니다."""
    # (실제 크롤링 로직 대신 서브에이전트가 크롤링해온 데이터를 사용합니다)
    menu_info = {
        "date": "2026년 4월 1일 (수요일)",
        "student_cafeteria": {
            "breakfast": "햄참치마요덮밥, 하늘보리",
            "lunch_korean": "순살안동찜닭, 미역국, 쌀밥, 감자고로케(케찹), 비빔막국수, 배추김치",
            "lunch_western": "미트소스스파게티, 크림스프, 후리가케밥, 프렌치토스트, 샐러드(드레싱), 배추김치",
            "snack": "불닭크림떡볶이, 튀김, 단무지"
        },
        "staff_cafeteria": {
            "lunch": "오징어깻잎볶음, 소고기뭇국, 메밀전병구이, 메추리알조림, 들기름비빔국수, 배추김치"
        }
    }
    return menu_info

def format_menu_message(menu):
    """식단 데이터를 텔레그렘 메시지용 텍스트로 변환합니다."""
    message = f"🏫 *신구대학교 오늘의 식단*\n📅 {menu['date']}\n\n"
    
    message += "🍱 *학생식당(서관)*\n"
    message += f"• 조식: {menu['student_cafeteria']['breakfast']}\n"
    message += f"• 중식(한식): {menu['student_cafeteria']['lunch_korean']}\n"
    message += f"• 중식(양식): {menu['student_cafeteria']['lunch_western']}\n"
    message += f"• 분식: {menu['student_cafeteria']['snack']}\n\n"
    
    message += "☕ *교직원식당*\n"
    message += f"• 중식: {menu['staff_cafeteria']['lunch']}\n\n"
    
    message += "맛있게 드세요! 😋"
    return message

def send_to_telegram(text):
    """텔레그렘으로 메시지를 전송합니다."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    data_json = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data_json, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result.get("ok", False)
    except Exception as e:
        print(f"전송 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("📋 식단 정보를 가져오는 중...")
    menu = get_today_menu()
    formatted_text = format_menu_message(menu)
    
    print("🚀 텔레그렘으로 전송 시도 중...")
    if send_to_telegram(formatted_text):
        print("✅ 성공: 오늘의 식단이 텔레그렘으로 전송되었습니다!")
    else:
        print("❌ 실패: 메시지 전송에 실패했습니다.")
