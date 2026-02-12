# from google import genai
# from config import Config
#
# aclient = genai.Client(api_key=Config.GEMINI_KEY).aio
# # client = genai.Client(api_key=Config.GEMINI_KEY)
# # for model in client.models.list():
# #     print(f"- {model.name}")
#
# async def set_prompt(prompt, model_ai):
#     response = await aclient.models.generate_content(
#         model=model_ai,
#         contents=prompt
#     )
#     await aclient.aclose()
#     return response.text

import asyncio
from gigachat import GigaChat
from config import Config



def get_giga_client(model):
    return GigaChat(
        credentials=Config.GIGACHAT_API_KEY,
        verify_ssl_certs=False,
        model=model
    )

async def send_prompt(prompt, model_ai="GigaChat-2"):
    loop = asyncio.get_event_loop()
    client = await loop.run_in_executor(None, get_giga_client, model_ai)

    try:
        response = await loop.run_in_executor(
            None,
            lambda: client.chat(prompt)
        )

        return response.choices[0].message.content
    finally:
        await loop.run_in_executor(None, client.close)

