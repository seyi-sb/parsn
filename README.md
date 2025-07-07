## 📡 PARSN 

**Parsn** is a fully automated website that updates itself with fresh tech news, smart tips, and DIY content — no manual work needed.

It’s like a robot editor: it checks trusted news sources, picks out the latest stories, grabs images, writes a short summary, and updates the homepage — all by itself.

---

### ⚙️ How the Automation Works

Every few hours, a Python script (`fetcher.py`) runs and:

1. **Collects** new articles from tech news feeds  
2. **Summarizes** the content using natural language tools  
3. **Finds an image** either from the article or using smart fallback options  
4. **Renders the homepage** with updated summaries, links, and images  
5. **Saves the updates** to your GitHub repo (and live site if hosted)

This process can run:
- ✅ Locally on your own computer (e.g. on your Mac)
- ✅ Automatically in the cloud via **GitHub Actions** (so your site updates even if you're asleep)

---

### 🧠 Why Parsn?

- No database  
- No backend server  
- No logging in  
- Just **clean, updated content** pulled from real tech sites  
- Perfect for info-lovers, indie creators, or anyone who wants a hands-off solution

---

### 💡 Built With

- Python  
- Jinja2 (for templating the site layout)  
- feedparser (to read RSS feeds)  
- sumy (for AI-based summarization)  
- GitHub Actions (for optional automation)

---

### 🔮 Future Updates

Parsn is still growing. Here's what’s planned for upcoming versions:

- 📝 **Dedicated article pages**  
  Each story will have its own page with a unique URL (slug) like `articles/ai-will-change-jobs.html`.

- 🧠 **More advanced summaries**  
  Future versions will use multiple AI models to generate deeper, more human-like summaries.

- 📖 **Detailed full-text articles**  
  The system will create longer, more readable content — with the potential to support ads and AdSense.

- 🔍 **Search and filter**  
  Visitors will be able to search and sort stories by topics or keywords.

- 🧰 **Personalized toolkits and widgets**  
  Plans to add extra features like tech tools, newsletter signups, or productivity widgets.

- 🚀 **Parsn Pack (Starter Kit)**  
  A plug-and-play version that lets anyone launch their own automated content site in minutes.
