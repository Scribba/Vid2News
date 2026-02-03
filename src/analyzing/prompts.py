NEWS_ANALYSIS_PROMPT_TEMPLATE = """
Your task is to analyze the given news-style post and determine whether it is suitable for publication.

Perform the analysis across three dimensions:

1. Factual and logical correctness:
- Is the content logically coherent?
- Are there internal contradictions?
- Are there obvious factual errors or misleading statements?
- Does the text contain hallucinations, vague claims, or generic LLM-style filler?

2. News structure and quality:
- Does the post have a clear informational structure?
- Does it avoid unnecessary digressions or "fluff"?
- Is it concrete and specific rather than abstract?
- Does it resemble a news item rather than an essay or opinion?

3. Informational value and relevance:
- Is the information important?
- Does it bring something new or useful?
- Does it refer to a real, current event or trend?
- Would it be interesting for a general audience?

Return ONLY a valid JSON object in the following format:

{{
  "approved": true or false,
  "score": integer from 1 to 10
}}

Rules:
- Set "approved" to false if there are major logical, factual, or structural issues, or if the content is too vague or generic.
- Score scale:
  1–2: no real informational value  
  3–4: very generic, weak  
  5–6: acceptable but average  
  7–8: strong, valuable news  
  9–10: highly important, breakthrough event  

Do not rewrite or improve the post.
Do not include any text outside the JSON.
Be critical and skeptical — do not assume the content is correct.

Post to analyze:
TITLE: {title}
CONTENT: {content}

"""