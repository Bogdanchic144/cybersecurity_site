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



# import asyncio
# import os
#
# async def get_ai():
#     client = AsyncOpenAI(
#         # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
#         api_key=os.getenv("DASHSCOPE_API_KEY"),
#         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
#     )
#
#     completion = await client.chat.completions.create(
#         # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
#         model="qwen-plus",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "privet"},
#         ]
#     )
#     print(completion.model_dump_json())
#
# asyncio.run(get_ai())