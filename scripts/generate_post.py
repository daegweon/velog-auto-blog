import os
import requests
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("CHATGPT_API_KEY"))

def get_trending_keyword():
    api_key = os.getenv("NEWS_API_KEY")
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "language": "en",
        "pageSize": 10,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("status") != "ok":
            raise ValueError("NewsAPI error")

        articles = data.get("articles", [])
        if not articles:
            raise ValueError("No articles found")

        titles = [article["title"] for article in articles if article.get("title")]
        trending_keyword = titles[0].split(":")[0].strip()
        print(f"[✔] Trending keyword from news: {trending_keyword}")
        return trending_keyword

    except Exception as e:
        print(f"[!] NewsAPI trend fetch failed: {e}")
        return "Latest Technology Trends in 2025"

def generate_title(topic):
    prompt = f"Write a catchy blog post title about '{topic}' in less than 50 characters."
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def generate_content(topic):
    prompt = f"""
Write a detailed Markdown blog post about "{topic}" in English.

- At least 1,000 words
- Include 3 to 5 subheadings using ## style
- Use friendly and informative tone (not robotic)
- Add examples and tips under each section
- Include a summary at the end
"""
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def generate_image(topic):
    styles = [
        "photorealistic",
        "natural light",
        "real-world situation",
        "cinematic stock photo",
        "lifestyle photography"
    ]
    style = ", ".join(styles)
    prompt = f"A {style} of '{topic}', professional photography, no text, sharp focus"
    res = client.images.generate(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    return res.data[0].url

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
    create_markdown_file(title, topic, content, image_url)
