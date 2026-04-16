import urllib.request
import json

# -----------------------------------------------------------------------------
# 설정 / Configuration
# -----------------------------------------------------------------------------
# 파일에서 확인된 정보를 바탕으로 설정합니다
TELEGRAM_BOT_TOKEN = '8287561582:AAEpMXqxwTYUusa-xqnX_mttZNgM4pT4ERU'
TELEGRAM_CHAT_ID = '8672911639'

def test_telegram_bot():
    """텔레그램 봇 연동 테스트를 수행합니다."""
    print("--- 텔레그램 봇 테스트 시작 ---")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    message = "🤖 [테스트 메시지] 텔레그램 봇과 성공적으로 연결되었습니다!"
    
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    
    # 데이터를 JSON 형식으로 변환하고 UTF-8 인코딩
    data_json = json.dumps(data).encode('utf-8')
    
    # 요청 객체 생성 및 헤더 설정
    req = urllib.request.Request(url, data=data_json, headers={'Content-Type': 'application/json'})
    
    try:
        # API 호출
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            if result.get("ok"):
                print("✅ 결과: 메시지 전송 성공!")
                print(f"   (받는 사람 ID: {TELEGRAM_CHAT_ID})")
            else:
                print("❌ 결과: 실패 - " + result.get("description", "알 수 없는 오류"))
                
    except Exception as e:
        print(f"💥 오류 발생: {e}")
        print("\n[참고] 봇 연동이 실패했다면 다음 사항을 확인해 보세요:")
        print("1. 텔레그램 앱에서 봇을 검색해 '/start'를 눌렀나요?")
        print("2. 'telegram api 활용방법.txt'에 적힌 TOKEN과 ID가 맞나요?")
        print("3. 인터넷 연결 상태를 확인해 주세요.")

if __name__ == "__main__":
    test_telegram_bot()
