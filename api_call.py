from google import genai

client = genai.Client()

def api_call(contents):
    return client.models.generate_content(model="gemini-2.5-flash", contents=contents)