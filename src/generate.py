import os
print("========== GENERATE.PY LOADED ==========")
print(__file__)

from typing import List, Dict, Any
from groq import Groq

try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

PROMPT_TEMPLATE = """You are a precise, grounded AI assistant answering questions about an uploaded document.

CRITICAL INSTRUCTIONS:
1. Answer the question relying ONLY on the provided context below.
2. Do NOT assume, extrapolate, or use general knowledge not present in the context.
3. If the context does not contain sufficient information to answer the question, state exactly: "I cannot find the answer to your question in the uploaded document."
4. Keep your answer clear, direct, and concise.

---
DOCUMENT CONTEXT:
{context}
---

USER QUESTION: {query}

GROUNDED ANSWER:"""


def build_context_string(retrieved_results: List[Dict[str, Any]]) -> str:
    context_blocks = []
    for item in retrieved_results:
        chunk = item["chunk"]
        score = item.get("score", 0.0)
        block = f"[Source Chunk #{chunk['id']} (Relevance Score: {score:.2f})]:\n{chunk['text']}"
        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def generate_answer(
    query: str,
    retrieved_results: List[Dict[str, Any]],
    is_relevant: bool = True,
    provider: str = "auto",
    chat_history: List[Dict[str, str]] = None
) -> str:
    
    if not is_relevant or not retrieved_results:
        return "I cannot find any relevant information in the uploaded document to answer your question."

    context_str = build_context_string(retrieved_results)

    # BUG #3 INTRODUCED HERE FOR INTERNS TO DEBUG:
    # Passing empty string context="" instead of context=context_str!
    # Correct code should be: prompt = PROMPT_TEMPLATE.format(context=context_str, query=query)
    history_text = ""

def generate_answer(
    query: str,
    retrieved_results: List[Dict[str, Any]],
    is_relevant: bool = True,
    provider: str = "auto",
    chat_history: List[Dict[str, str]] = None
) -> str:

    if not is_relevant or not retrieved_results:
        return "I cannot find any relevant information in the uploaded document to answer your question."

    context_str = build_context_string(retrieved_results)

    history_text = ""

    if chat_history:
        for msg in chat_history[-6:]:
            history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
Previous Conversation:
{history_text}

""" + PROMPT_TEMPLATE.format(
        context=context_str,
        query=query
    )

    env_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    active_provider = provider if provider != "auto" else env_provider

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    print("=" * 50)
    
    print("Active Provider:", active_provider)
    print("HAS_GROQ:", HAS_GROQ)
    print("Groq Key Found:", bool(groq_key))
    print("=" * 50)
    
    if active_provider == "gemini" or (active_provider == "auto" and gemini_key):
        if HAS_GEMINI and gemini_key:
            return _call_gemini(prompt, gemini_key)
        elif openai_key and HAS_OPENAI:
            return _call_openai(prompt, openai_key)
        print("Provider:", active_provider)
        print("HAS_GROQ:", HAS_GROQ)
        print("Groq key exists:", bool(groq_key))

    elif active_provider == "openai" or (active_provider == "auto" and openai_key):
        if HAS_OPENAI and openai_key:
            return _call_openai(prompt, openai_key)
        elif gemini_key and HAS_GEMINI:
            return _call_gemini(prompt, gemini_key)
        
    elif active_provider == "groq":
        print("Provider is GROQ")
        print("HAS_GROQ =", HAS_GROQ)
        print("Groq Key =", bool(groq_key))
        return _call_groq(prompt, groq_key)
    
        print("Provider:", active_provider)
        print("HAS_GROQ:", HAS_GROQ)
        print("Groq key exists:", bool(groq_key))

    return _generate_mock_grounded_answer(query, retrieved_results)


def _call_gemini(prompt: str, api_key: str) -> str:
    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        import traceback
        return traceback.format_exc()


def _call_openai(prompt: str, api_key: str) -> str:
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with OpenAI API: {str(e)}"
    
def _call_groq(prompt: str, api_key: str) -> str:
    print("✅ INSIDE GROQ FUNCTION")
    
    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1024
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error communicating with Groq API: {str(e)}"


def _generate_mock_grounded_answer(query: str, retrieved_results: List[Dict[str, Any]]) -> str:
    best_chunk = retrieved_results[0]["chunk"]["text"]
    chunk_id = retrieved_results[0]["chunk"]["id"]

    return (
        f"[Demo / Offline Mode - No LLM API Key set]\n\n"
        f"Based on **Chunk #{chunk_id}** from the uploaded document:\n\n"
        f"> \"{best_chunk[:350]}...\"\n\n"
        f"*((To enable full natural-language generation, set `GROQ_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY` in your `.env` file.))*"
    )
