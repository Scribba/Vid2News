TRANSCRIPT_PARSING_PROMPT = """
You are an expert news analyst and content extractor.

Your task is to analyze a video transcript and extract **newsworthy information only**.

You must identify and extract distinct news items. For each news item, provide:
1. A clear, concise title
2. A brief summary (2–3 sentences)
3. The full content/details
4. Relevant keywords
5. Category (e.g., Technology, Politics, Business, Science, Entertainment, Sports, Health)
6. Named entities mentioned (people, organizations, locations, etc.)

Guidelines:
- Focus on factual, newsworthy information
- Ignore promotional content, ads, or filler
- Each news item must be self-contained
- Extract multiple news items if multiple topics are covered

---

Transcript:
{transcript_text}

---

Respond with **valid JSON only**, in **exactly** this format:

{{
  "news_items": [
    {{
      "title": "News headline",
      "summary": "Brief 2-3 sentence summary",
      "content": "Full details and context of the news",
      "keywords": ["keyword1", "keyword2"],
      "category": "Category name",
      "entities": ["Entity1", "Entity2"]
    }}
  ]
}}

If no newsworthy content is found, respond with:
{{"news_items": []}}
"""