import openai
import re
import os

# Make sure your OpenAI API key is set in environment as OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_oai(system_prompt_str, user_text_str=""):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt_str},
                {"role": "user", "content": user_text_str}
            ],
            temperature=0,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"```json\n{{\"event_found\": false, \"error\": \"{str(e)}\"}}\n```"

def extract_block(response_text_str):
    match = re.search(r"```json\s*\n(.*?)\n\s*```", response_text_str, re.DOTALL)
    if match:
        return match.group(1).strip()
    match_direct_json = re.search(r"(\{.*?\})", response_text_str, re.DOTALL)
    if match_direct_json:
        return match_direct_json.group(1).strip()
    return ""
