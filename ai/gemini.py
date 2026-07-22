import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.0-flash",
]

def ask_gemini(context, question):
    prompt = f"""
You are an Industrial Knowledge AI assistant.

Answer ONLY using the uploaded document.

Return your answer in clean HTML using:

<h3> headings
<ul> bullet points
<li> list items
<p> paragraphs

Do not use Markdown (**).

Document:
{context}

Question:
{question}
"""

    for model_name in MODELS:
        try:
            print(f"Trying model: {model_name}")

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            print(f"Success with: {model_name}")

            return response.text

        except Exception as e:
            print(f"{model_name} failed: {e}")

    return "<p><b>All Gemini models are currently unavailable.</b></p>"