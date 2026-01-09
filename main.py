# Главный файл приложения

import sys
from gui import FinancialApp

def main():
    """Запуск приложения"""
    try:
        app = FinancialApp()
        app.run()
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()