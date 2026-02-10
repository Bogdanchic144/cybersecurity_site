from google import genai
from config import Config

aclient = genai.Client(api_key=Config.GEMINI_KEY).aio
# client = genai.Client(api_key=Config.GEMINI_KEY)
# for model in client.models.list():
#     print(f"- {model.name}")

async def set_prompt(prompt, model_ai):
    response = await aclient.models.generate_content(
        model=model_ai,
        contents=prompt
    )
    await aclient.aclose()
    return response.text