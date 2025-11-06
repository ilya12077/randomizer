import pandas as pd
import json


def excel_to_json_format(file_path, output_file='prizes.json'):
    """
    Преобразует Excel файл с промокодами в JSON формат

    Args:
        file_path (str): путь к Excel файлу
        output_file (str): имя выходного JSON файла
    """

    # Читаем Excel файл
    df = pd.read_excel(file_path, header=None)

    # Создаем структуру JSON
    result = {
        "40": {
            "odds": "0.3",
            "codes": df.iloc[1:, 1].dropna().tolist()  # Столбец C (скидка 40%)
        },
        "30": {
            "odds": "0.2",
            "codes": df.iloc[1:, 2].dropna().tolist()  # Столбец C (скидка 30%)
        },
        "50": {
            "odds": "0.5",
            "codes": df.iloc[1:, 0].dropna().tolist()  # Столбец A (скидка 50%)
        }
    }

    # Сохраняем в JSON файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Файл сохранен как: {output_file}")
    return result


# Использование:
if __name__ == "__main__":
    # Укажите путь к вашему файлу
    file_path = "Промокоды_КН_Ноябрьская_распродажа.xlsx"

    # Основной способ (требует pandas)
    result = excel_to_json_format(file_path)

    # Показать статистику
    print(f"Промокодов 50%: {len(result['50']['codes'])}")
    print(f"Промокодов 30%: {len(result['30']['codes'])}")
    print(f"Промокодов 40%: {len(result['40']['codes'])}")
