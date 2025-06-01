import os

from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🎯 오늘 요일 가져오기
def get_today_name():
    return datetime.now().strftime('%A')

# 📡 오늘 수업 크롤링
def find_today_schedule():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.1milliondance.com/schedule/week")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
        )

        cards = driver.find_elements(By.TAG_NAME, "li")
        schedule_list = []

        last_minutes = None
        gap_threshold = 180  # 3시간

        for card in cards:
            try:
                time_elem = card.find_element(By.CLASS_NAME, "time")
                time_text = time_elem.text.replace("\xa0", " ").strip()

                teacher_buttons = card.find_elements(By.CLASS_NAME, "day-mid")
                if not teacher_buttons:
                    continue

                teacher_btn = teacher_buttons[0].find_element(By.TAG_NAME, "button")
                teacher_text = teacher_btn.text.strip()
                if not teacher_text:
                    continue

                full_line = f"{time_text} {teacher_text}"
                time_str = " ".join(full_line.split()[1:6])  # e.g. 3:30 - 4:50 PM (KST)
                start_minutes = parse_start_minutes(time_str)
                if start_minutes is None:
                    continue

                # ➤ gap이 너무 크거나, 시간이 되돌아가는 경우 중단
                if last_minutes is not None and (start_minutes + gap_threshold < last_minutes):
                    break

                schedule_list.append(full_line)
                last_minutes = start_minutes

            except Exception:
                continue

        return schedule_list

    except Exception as e:
        print("❌ 수업 정보를 불러오는 중 오류 발생:", str(e))
        return []
    finally:
        driver.quit()


# 📋 결과 출력
def parse_start_minutes(time_str):
    try:
        # 예: "3:30 - 4:50 PM (KST)"
        parts = time_str.split("-")
        start_part = parts[0].strip()           # "3:30"
        end_part = parts[1].strip()             # "4:50 PM (KST)"

        # "4:50 PM (KST)" → "PM"
        meridiem = "AM" if "AM" in end_part else "PM"

        hour, minute = map(int, start_part.split(":"))

        if meridiem == "PM" and hour != 12:
            hour += 12
        elif meridiem == "AM" and hour == 12:
            hour = 0

        return hour * 60 + minute
    except:
        return None
import re
from datetime import datetime

def format_time_range(text):
    """
    '3:30 - 4:50 PM' → '3:30-4:50(PM)' 형식으로 변환
    """
    match = re.search(r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*(AM|PM)', text)
    if match:
        start, end, period = match.groups()
        return f"{start}-{end}({period})"
    return text

def print_today_schedule(schedule):
    if not schedule or len(schedule) <= 1:
        print("오늘은 원밀리언 수업이 없습니다.")
        return

    print(f"\n📅 오늘({datetime.now().day}일)의 원밀리언 수업 일정\n")
    print("\n   ⏰ TIME \t  💁DANCER")

    last_start_minutes = None
    gap_threshold = 180  # 3시간 기준

    for idx, line in enumerate(schedule[:-1], start=1):
        time_str = " ".join(line.split()[1:6])
        start_minutes = parse_start_minutes(time_str)

        if start_minutes is None:
            continue

        # 3시간 이상 과거로 돌아가면 "다음 날 수업"으로 간주하고 중단
        if last_start_minutes is not None and start_minutes + gap_threshold < last_start_minutes:
            break

        # ✂️ 불필요한 정보 제거
        cleaned_line = re.sub(r"(1F|2F)\s+", "", line)  # 층 정보 제거
        cleaned_line = cleaned_line.replace("(KST)", "").strip()  # 시간대 제거

        # 🕒 시간 포맷 변환
        cleaned_line = re.sub(
            r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*(AM|PM)',
            lambda m: f"{m.group(1)}-{m.group(2)}({m.group(3)})",
            cleaned_line
        )

        print(f"{idx}. {cleaned_line}")
        last_start_minutes = start_minutes

    print("\n⸻\n")

# 🔑 OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎉 인트로
print("💬 댄스 클래스 큐레이터에 오신 걸 환영합니다!\n관심 있는 댄스 장르가 있으신가요?\n해당 장르에 유명한 댄서를 알려드리고 댄스 스튜디오을 추천해드립니다.\n")
print("➕ 오늘의 원밀리언 댄스 스튜디오 시간표를 보고 싶으시면 '원밀리언 오늘 수업'과 같이 입력해주세요\n")
print("'help'를 입력하시면 질문 작성 예시를 보여드리며,\n'quit'를 입력하시면 종료됩니다.\n")
print("참고할 만한 장르: 힙합, 힐코레오, 재즈, 왁킹, 팝핀, 락킹, 하우스, 어반, 코레오")

while True:
    user_input = input("👤 질문: ").strip()

    if user_input.lower() == "quit":
        print("👋 프로그램을 종료합니다.")
        break
    elif user_input.lower() == "help":
        print("\n입력 예시:\n  - 1. 힙합 장르로 유명한 댄서 수업을 추천\n  - 2. 힐코레오 배우고 싶어\n  - 3. 오늘 원밀리언 수업 일정 알려줘\n")
        continue

    # ✅ [추가] 오늘 수업 관련 키워드 감지
    if "오늘" in user_input and ("수업" in user_input or "일정" in user_input):
        print("🔍 오늘의 원밀리언 수업을 가져오는 중...\n")
        try:
            schedule = find_today_schedule()
            print_today_schedule(schedule)
        except Exception as e:
            print("❌ 수업 정보를 불러오는 중 오류 발생:", str(e))
        continue  # GPT 호출 생략

    print("\n🔍 사용자 입력 분석 중…")
    print("📡 관련 내용 검색 중…\n")

    # GPT 호출
    system_prompt = """
당신은 댄스 클래스 큐레이터입니다.
사용자의 요청에 따라 처리, 응답하세요:
사용자가 장르의 유명한 댄서를 알고 싶다고 하면 그에 해당하는 유명한 한국인 댄서(가수 제외) 2~3명을 소개하면서 그들의 수업을 추천하세요.

첫 번째 조건에 해당하는 경우, 출력 형식은 아래 예시를 따르세요:

📣 해당 장르의 대표 댄서:
- Lia Kim
- Kasper

💬 댄서에 대한 정보:
- Lia Kim은 ...
- Kasper는 ..

💃 추천 수업 #1:
    • 학원명: ...
    • 댄서: ...
    • 위치: ...
    
💬 추천 사유: ...

—
🕺 추천 수업 #2:
    • 학원명: ...
    • 댄서: ...
    • 위치: ...
    
💬 추천 사유: ...
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip()

        if content:
            print(content)
            print("\n⸻\n")
        else:
            print("⚠️ 유효하지 않은 입력입니다. 다시 입력해주세요.\n")

    except Exception as e:
        print("❌ 오류 발생:", str(e))