import aiohttp
import asyncio

from pathlib import Path
from config import Config


def escape_markdown_v2(text: str) -> str:
    translation_table = str.maketrans({
        '_': r'\_',
        '*': r'\*',
        '[': r'\[',
        ']': r'\]',
        '(': r'\(',
        ')': r'\)',
        '~': r'\~',
        '`': r'\`',
        '>': r'\>',
        '#': r'\#',
        '+': r'\+',
        '-': r'\-',
        '=': r'\=',
        '|': r'\|',
        '{': r'\{',
        '}': r'\}',
        '.': r'\.',
        '!': r'\!'
    })

    return text.translate(translation_table)

def delete_file(name: str):
    script_dir = Path(__file__).parent.parent
    target_dir = script_dir / "app"
    file_path = target_dir / name
    if file_path.is_file():
        file_path.unlink()

async def get_file_info(file_name: str) -> str:
    script_dir = Path(__file__).parent.parent
    target_dir = script_dir / "app"

    file_path = target_dir / file_name
    if not file_path.is_file():
        print("Файл не найден!")
        return r"Произошла ошибка\, файл не обнаружен \(возможно такой файл не поддерживается\)"

    async with aiohttp.ClientSession() as session:
        try:
            # 1. ЗАГРУЖАЕМ tvoyamama as file
            url = "https://www.virustotal.com/api/v3/files"
            headers = {
                "accept": "application/json",
                "x-apikey": Config.VT_KEY
            }

            with open(file_path, "rb") as f:
                file_content = f.read()

            form_data = aiohttp.FormData()
            form_data.add_field('file',
                                file_content,
                                filename=file_name,
                                content_type='application/octet-stream')

            async with session.post(url, headers=headers, data=form_data) as response:
                if response.status != 200:
                    return escape_markdown_v2(rf"❌ Ошибка загрузки: {response.status}")

                data: dict = await response.json()
                analysis_id = data['data']['id']
                print(f"✅ Файл загружен, analysis_id: {analysis_id}")

            # STEP 2. ЖДЕМ
            analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"

            max_retries = 10
            for attempt in range(max_retries):
                async with session.get(analysis_url, headers=headers) as analysis_response:
                    analysis_data: dict = await analysis_response.json()
                    status = analysis_data['data']['attributes']['status']

                    if status == 'completed':
                        print(f"✅ Анализ завершен (попытка {attempt + 1})")
                        break
                    elif status == 'queued':
                        print(f"⏳ Анализ в очереди... (попытка {attempt + 1}/{max_retries})")
                        await asyncio.sleep(15)
                    else:
                        print(f"📊 Статус анализа: {status}")
                        await asyncio.sleep(15)
            else:
                return r"⚠️ Анализ не завершился за отведенное время\, попробуйте ещё раз"

            # STEP 3. НАСЛАЖДАЕМСЯ
            return format_analysis_result(analysis_data)

        except Exception as e:
            return escape_markdown_v2(f"❌ Ошибка: {str(e)}")

        finally:
            file_path.unlink()
def format_analysis_result(analysis_data) -> str:
    stats = analysis_data['data']['attributes']['stats']
    file_info = analysis_data['meta']['file_info']
    results = analysis_data['data']['attributes']['results']

    lines_one = [
        rf"📊 *Статистика анализа*\:",
        rf"     Вредоносных\: {stats['malicious']}",
        rf"     Подозрительных\: {stats['suspicious']}",
        rf"     Необнаружено\: {stats['undetected']}",
        rf"     Безопасных\: {stats['harmless']}"
    ]

    part_one = "\n".join(lines_one)

    lines_two = [
        rf"📁 *Информация о файле*\:",
        rf"     SHA256\: `{file_info['sha256']}`",
        rf"     MD5\: `{file_info['md5']}`",
        rf"     Размер\: {file_info['size']} байт"
    ]

    part_two = "\n".join(lines_two)

    # Детекты
    detections = []
    for av_name, result in results.items():
        if result['category'] in ['malicious', 'suspicious'] and result['result']:
            detections.append(escape_markdown_v2(
                                                f"    • {av_name}:") +
                                                f"""_{escape_markdown_v2(f" {result['result']}")}_"""
                                                 )

    if detections:
        part_three = rf"⚠️ *Обнаружения угроз*\:" + "\n" + "\n\n".join(detections)
    else:
        part_three = f"\n✅ Угроз не обнаружено"

    return "#S0S#".join([part_one, part_two, part_three])