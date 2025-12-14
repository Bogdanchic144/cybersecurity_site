import vt

from config import VT_KEY

with vt.Client(VT_KEY) as client:
    def scan_local_file(client, file_path, wait=False):
        """
        Загрузка и сканирование локального файла

        Args:
            client: Клиент vt-py
            file_path: Путь к файлу
            wait: Ожидать завершения анализа
        """
        try:
            with open(file_path, "rb") as file:
                analysis = client.scan_file(
                    file,
                    wait_for_completion=wait
                )

                if wait:
                    print(f"Анализ завершен. ID: {analysis.id}")
                    print(f"Статус: {analysis.status}")

                    result = client.get_object(f"/analyses/{analysis.id}")
                    return result
                else:
                    print(f"Анализ запущен. ID: {analysis.id}")
                    return analysis

        except FileNotFoundError:
            print(f"Файл не найден: {file_path}")
            return None
        except vt.APIError as e:
            print(f"Ошибка загрузки файла: {e}")
            return None

    print(scan_local_file(client, "files/test.py"))