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





# async def set_prompt(prompt):
#     client = AsyncOpenAI(api_key=Config.DEEPSEEK_KEY, base_url="https://api.deepseek.com")
#
#     response = await client.chat.completions.create(
#         model="deepseek-chat",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant"},
#             {"role": "user", "content": prompt},
#         ],
#         stream=False
#     )
#     return response.choices[0].message.content
#
# print(asyncio.run(set_prompt("privet")))