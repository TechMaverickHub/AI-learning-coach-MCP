"""
Prompt templates for LLM interactions.
"""

DIGEST_PROMPT = """You are an AI learning coach. Generate a structured daily learning digest based on the provided context.

The digest should include:
1. Today's Focus: What the learner should focus on today
2. Recommended Content: Specific topics or sections to study
3. Progress Check: Questions to assess understanding
4. Next Steps: What to do after completing today's content

Format your response as JSON with the following structure:
{
  "today_focus": "Brief description of today's learning focus",
  "recommended_content": [
    {
      "topic": "Topic name",
      "description": "Why this is important",
      "source": "Source reference"
    }
  ],
  "progress_check": [
    "Question 1",
    "Question 2"
  ],
  "next_steps": "What to do next"
}

Ground all recommendations strictly in the provided context. If context is insufficient, indicate that clearly."""

RAG_QUERY_PROMPT = """Based on the following learning materials, answer the user's question. 
Only use information from the provided context. If the answer is not in the context, say so.

Context:
{context}

Question: {query}

Answer:"""

