from openai import OpenAI
import os
from datetime import datetime
from pytrends.request import TrendReq

client = OpenAI(api_key=os.getenv("CHATGPT_API_KEY"))

HIGH_PROFIT_KEYWORDS = [
    "보험", "대출", "신용카드", "건강검진", "자동차 보험",
    "전세보증금", "명의이전", "자기계발", "공무원 시험", "이직",
    "가전제품", "스마트폰", "노트북", "청약"
]

def get_trending_keyword():
    pytrends = TrendReq(hl='ko', tz=540)
    try:
        pytrends.build_payload(kw_list=["건강검진"])
        related = pytrends.related_queries()
        suggestions = related.get("건강검진", {}).get("top")
        if suggestions is not None:
            for kw in suggestions["query"].tolist():
                if any(p in kw for p in HIGH_PROFIT_KEYWORDS):
                    return kw
    except Exception as e:
        print("[!] 트렌드 키워드 분석 실패:", e)
    return "2025 건강검진 꿀팁"

def generate_title(topic):
    prompt = f"'{topic}'을 주제로 Velog 블로그 글 제목을 만들어줘. 50자 이내."
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def generate_content(topic):
    prompt = f"'{topic}'에 대한 블로그 글을 마크다운 형식으로 작성해줘. 소제목 포함, 5문단 이상."
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def generate_image(topic):
    res = client.images.generate(
        prompt=f"{topic}에 어울리는 일러스트 썸네일",
        n=1,
        size="512x512"
    )
    return res.data[0].url

def insert_affiliate_link(topic, content):
    partner_id = os.getenv("COUPANG_PARTNER_ID", "demo")
    link = f"https://link.coupang.com/refer?key={topic}&pid={partner_id}"
    ad = f"[{topic} 관련 추천 상품 보러가기]({link})"
    return content + f"\n\n---\n\n{ad}"

def create_markdown_file(title, topic, content, image_url):
    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"markdown/{today}-{title.replace(' ', '_')}.md"
    os.makedirs("markdown", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""---
title: {title}
description: {topic}에 대한 실속 정보
tags: [트렌드, 정보, 꿀팁]
date: {today}
---

![썸네일]({image_url})

{content}
""")
    print(f"[✔] 마크다운 저장 완료: {filename}")

if __name__ == "__main__":
    topic = get_trending_keyword()
    title = generate_title(topic)
    content = generate_content(topic)
    image_url = generate_image(topic)
    content = insert_affiliate_link(topic, content)
    create_markdown_file(title, topic, content, image_url)
