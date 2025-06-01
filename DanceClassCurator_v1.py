import os
from openai import OpenAI

# 클라이언트 초기화 (최신 방식)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("💬 댄스 클래스 큐레이터에 오신 걸 환영합니다!\n관심 있는 댄스 장르가 있으신가요?\n해당 장르에 유명한 댄서를 알려드리고 수업을 추천해드립니다.\n")
print("'help'를 입력하시면 질문 작성 예시를 보여드리며,\n'quit'를 입력하시면 종료됩니다.\n")
print("참고할 만한 장르: 힙합, 힐코레오, 재즈, 왁킹, 팝핀, 락킹, 하우스, 어반, 코레오")

while True:
    user_input = input("👤 질문: ").strip()

    if user_input.lower() == "quit":
        print("👋 프로그램을 종료합니다.")
        break
    elif user_input.lower() == "help":
        print("\n입력 예시:\n  - 1. 힙합 장르로 유명한 댄서 수업을 추천 \n  - 2. 힐코레오 배우고 싶어 \n - 3. 원밀리언 소속 댄서 중 힙합 댄서 추천해줘\n")
        continue

    print("\n🔍 사용자 입력 분석 중…")
    print("📡 관련 내용 검색 중…\n")

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

        print(response.choices[0].message.content)
        print("\n⸻\n")

    except Exception as e:
        print("❌ 오류 발생:", str(e))