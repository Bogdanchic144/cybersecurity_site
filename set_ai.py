# from gigachat import GigaChat
import openai
from openai import AsyncOpenAI
from config import Config

async def set_prompt(prompt, model_ai):
    client = AsyncOpenAI(
        api_key=f"{Config.GEMINI_KEY}",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    try:
        response = await client.chat.completions.create(
            model=f"gemini-2.5-{model_ai}",
            messages=[{"role": "user", "content": prompt}]
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"Ошибка: {e}"

# async def set_prompt(level):
#     giga = GigaChat(
#         credentials="M2Q4ZGUwMGYtMTBkZi00NmM5LTg0NzAtODFjNDM5OWFlOGY3OjlhMzg2MDczLTdhOWYtNGE5Yy05ZTFkLTk5MTI0NzAzNjJlNw==",
#         verify_ssl_certs=False,
#         ssl_context_factory=lambda: ssl._create_unverified_context()
#     )
#     responce = await giga.achat(f"{word_text}\nСоставь {level} задание") # сложное/среднее/легкое
#     print(responce.choices[0].message.content)
#     return responce.choices[0].message.content


