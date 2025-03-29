from openai import OpenAI
import os
from datetime import datetime
from pytrends.request import TrendReq

client = OpenAI(api_key=os.getenv("CHATGPT_API_KEY"))

def get_trending_keyword():
    pytrends = TrendReq(hl='ko', tz=540)
    try:
        # 한국은 지원 안 되므로 미국 트렌드 사용
        trending = pytrends.trending_searches(pn='united_states')
        keyword = trending[0]  # 가장 상단 인기 키워드
        print(f"[✔] 트렌딩 키워드 추출: {keyword}")
        return keyword
    except Exception as e:
        print(f"[!] 트렌드 분석 실패: {e}")
        return "2025 건강검진 꿀팁"

def generate_title(topic):
    prompt = f"Write a catchy blog post title about '{topic}' in less than 50 characters."
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def generate_content(topic):
    prompt = f"""
Write a detailed and informative Markdown blog post about "{topic}" in English.

Guidelines:
- Write at least 1000 words
- Use 3 to 5 subheadings (## format)
- Under each subheading, include 2–3 paragraphs with helpful content
- Use a friendly and human-like tone (not robotic)
- Add practical tips, examples, or interesting facts where possible
- Include a brief summary or conclusion at the end
"""
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def generate_image(topic):
    prompt = f"A modern, clean blog thumbnail about '{topic}', in icon or illustration style, with a bright background, no text"
    res = client.images.generate(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    return res.data[0].url

def insert_affiliate_link(topic, content):
    partner_id = os.getenv("COUPANG_PARTNER_ID", "demo")
    link = f"https://link.coupang.com/refer?key={topic}&pid={partner_id}"
    ad = f"[Check out recommended products related to {topic}]({link})"
    return content + f"\n\n---\n\n{ad}"

def create_markdown_file(title, topic, content, image_url):
    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"markdown/{today}-{title.replace(' ', '_')}.md"
    os.makedirs("markdown", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""---
title: {title}
description: A helpful blog post about {topic}
tags: [trending, guide, tips]
date: {today}
---

![Thumbnail]({image_url})

{content}
""")
    print(f"[✔] Markdown saved: {filename}")

if __name__ == "__main__":
    topic = get_trending_keyword()
    title = generate_title(topic)
    content = generate_content(topic)
    image_url = generate_image(topic)
    #content = insert_affiliate_link(topic, content)
    create_markdown_file(title, topic, content, image_url)
