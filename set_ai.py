# from gigachat import GigaChat
from openai import AsyncOpenAI

# import ssl

async def set_prompt(prompt):
    client = AsyncOpenAI(
        api_key="AIzaSyBZC5yUUTvrIbKguiio5WvFk3FBTdlGwbg",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    try:
        response = await client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# async def set_prompt(level):
#     giga = GigaChat(
#         credentials="M2Q4ZGUwMGYtMTBkZi00NmM5LTg0NzAtODFjNDM5OWFlOGY3OjlhMzg2MDczLTdhOWYtNGE5Yy05ZTFkLTk5MTI0NzAzNjJlNw==",
#         verify_ssl_certs=False,
#         ssl_context_factory=lambda: ssl._create_unverified_context()
#     )
#     responce = await giga.achat(f"{word_text}\nСоставь {level} задание") # сложное/среднее/легкое
#     print(responce.choices[0].message.content)
#     return responce.choices[0].message.content


