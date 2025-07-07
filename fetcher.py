import time
import feedparser
import os, json
import re
import requests
import random
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from feeds_config import rss_feeds
from rake_nltk import Rake
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from bs4 import BeautifulSoup
from slugify import slugify  # pip install python-slugify
from newspaper import Article
from dateutil import parser

UNSPLASH_ACCESS_KEY = "pjuyEr1YqaYaX1o5viB6zP65iI_hyAXVyMebrqKok1o"
rake = Rake()

def paraphrase_title(title):
    replacements = {
        "launches": ["unveils", "releases", "rolls out", "introduces"],
        "announces": ["reveals", "shares", "discloses"],
        "reveals": ["uncovers", "presents", "highlights"],
        "AI": ["artificial intelligence", "AI-based", "machine learning"],
        "tool": ["platform", "solution", "app"],
        "update": ["refresh", "revision", "upgrade"],
        "feature": ["function", "capability", "option"],
        "platform": ["service", "ecosystem"],
        "report": ["findings", "brief", "summary"],
        "says": ["notes", "mentions", "claims"]
    }

    words = title.split()
    new_words = []

    for word in words:
        key = word.lower()
        if key in replacements:
            # Preserve original capitalization
            replacement = random.choice(replacements[key])
            if word[0].isupper():
                replacement = replacement.capitalize()
            new_words.append(replacement)
        else:
            new_words.append(word)

    # Swap simple structure e.g. "Google releases tool" → "Tool released by Google"
    if "by" not in title.lower() and len(new_words) > 2:
        if new_words[0][0].isupper():  # likely a company or name
            new_words = new_words[1:] + ["by", new_words[0]]

    return " ".join(new_words)


def get_full_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"[!] Failed to extract full article from {url}: {e}")
        return ""

def generate_slug(title):
    return slugify(title)

def summarize_full_text(text, sentence_count=10):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)

def get_summary(html_text, sentence_count=3):
    plain_text = BeautifulSoup(html_text, "html.parser").get_text()
    parser = PlaintextParser.from_string(plain_text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary_sentences = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary_sentences)

def get_fallback_image(summary):
    rake.extract_keywords_from_text(summary)
    keywords = rake.get_ranked_phrases()
    if not keywords:
        keywords = ["technology"]
    query = keywords[0]
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={UNSPLASH_ACCESS_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        results = data.get("results", [])
        if results:
            return results[0]["urls"]["small"]
    except Exception as e:
        print(f"Unsplash API error: {e}")
    return "https://via.placeholder.com/300?text=No+Image"

def get_article_top_image(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.top_image  # This usually returns the main image URL
    except Exception as e:
        print(f"[!] Failed to get top image from {url}: {e}")
        return ""

def extract_image(entry):
    # 1. Try to extract from HTML inside summary/content
    html_source = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
    soup = BeautifulSoup(html_source, "html.parser")
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src", "").startswith("http"):
        return img_tag["src"]

    # 2. Try known structured fields
    if "media_content" in entry and len(entry.media_content) > 0:
        url = entry.media_content[0].get("url", "")
        if url.startswith("http"):
            return url

    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        url = entry.media_thumbnail[0].get("url", "")
        if url.startswith("http"):
            return url

    if "image" in entry:
        url = entry["image"].get("href", "")
        if url.startswith("http"):
            return url

    # 3. If all fail, use fallback image
    return get_fallback_image(html_source)


def parse_date(date_str):
    try:
        return parser.parse(date_str)
    except Exception:
        return None

def fetch_all_feeds(feed_urls):
    articles = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            original_title = entry.get("title", "No title")
            title = paraphrase_title(original_title)

            summary_raw = entry.get("summary", "No summary")
            summary_clean = BeautifulSoup(summary_raw, "html.parser").get_text()
            slug = generate_slug(title)
            link = entry.get("link", "#")

            full_article_text = get_full_article_text(link)
            if full_article_text.strip():
                full_summary = summarize_full_text(full_article_text, sentence_count=10)
            else:
                full_summary = summarize_full_text(summary_clean, sentence_count=3)
            
            image_url = extract_image(entry)
    
            if not image_url or "placeholder" in image_url:
                # Try to get the main image from the article page itself
                image_url = get_article_top_image(link)
                if not image_url:
                    image_url = get_fallback_image(summary_clean)

            article = {
                "title": title,
                "slug": slug,
                "link": link,
                "published": entry.get("published", "No date"),
                "image": extract_image(entry),
                "image": image_url,
                "summary": summary_clean,
                "full_text": full_summary,  # Kept in case you want to show a tooltip/preview
            }

            articles.append(article)
            
            

    return articles

def save_articles_to_json(articles, filename="articles.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

def render_html(articles, template_file="template.html", output_file="index.html"):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(template_file)
    rendered = template.render(articles=articles)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)

def main():
    start_time = time.time()  # ⏱ Start timer
    articles = fetch_all_feeds(rss_feeds)

    # Parse and sort by date
    for article in articles:
        article["published_parsed"] = parse_date(article["published"])
    articles = [a for a in articles if a["published_parsed"] is not None]
    articles.sort(key=lambda x: x["published_parsed"], reverse=True)
    for article in articles:
        article["published"] = article["published_parsed"].strftime("%Y-%m-%d %H:%M")
        del article["published_parsed"]

    save_articles_to_json(articles)
    render_html(articles)

    # 🕒 Print runtime in minutes
    end_time = time.time()
    elapsed_seconds = end_time - start_time
    elapsed_minutes = elapsed_seconds / 60
    print(f"\n✅ Finished in {elapsed_minutes:.2f} minutes")

if __name__ == "__main__":
    main()
