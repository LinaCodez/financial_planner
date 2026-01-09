import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models import FinanceManager, OperationType
from storage import DataStorage
from analysis import DataAnalyzer

class FinancialApp:
    """Главное окно приложения"""
    
    def __init__(self):
        """Инициализация приложения"""
        # Менеджеры
        self.manager = FinanceManager()
        self.storage = DataStorage()
        self.analyzer = DataAnalyzer(self.manager)
        
        # Переменные для сортировки и фильтрации
        self.sort_column = "date"
        self.sort_reverse = True
        self.current_filters = {}
        
        # Загрузка данных
        self.load_data()
        
        # Создание окна
        self.root = tk.Tk()
        self.root.title("Финансовый планировщик")
        self.root.geometry("1100x650")
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление данных
        self.refresh_all()
    
    def load_data(self):
        """Загрузка данных"""
        operations, next_id = self.storage.load_data()
        self.manager.operations = operations
        self.manager.next_id = next_id
    
    def save_data(self):
        """Сохранение данных"""
        self.storage.save_data(self.manager.operations)
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Панель ввода
        input_frame = ttk.LabelFrame(self.root, text="Новая операция", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Поля ввода
        fields = [
            ("Тип:", "type_var", ["расход", "доход"], True),
            ("Сумма:", "amount_var", None, False),
            ("Категория:", "category_var", None, False),
            ("Дата (ГГГГ-ММ-ДД):", "date_var", None, False),
            ("Описание:", "description_var", None, False),
        ]
        
        for i, (label, var_name, values, readonly) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            
            var = tk.StringVar()
            setattr(self, var_name, var)
            
            if values:  
                var.set(values[0])
                widget = ttk.Combobox(input_frame, textvariable=var, 
                                     values=values, width=18, state="readonly" if readonly else "normal")
            else: 
                if var_name == "date_var":
                    var.set(datetime.now().strftime("%Y-%m-%d"))
                widget = ttk.Entry(input_frame, textvariable=var, width=21)
            
            widget.grid(row=i, column=1, padx=5, pady=2, sticky="w")
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить", command=self.add_operation, 
                  width=20).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Панель фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Фильтры
        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, sticky="w")
        self.filter_type_var = tk.StringVar(value="все")
        ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                    values=["все", "доход", "расход"], width=10, 
                    state="readonly").grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.filter_category_var = tk.StringVar(value="все")
        self.filter_category_combo = ttk.Combobox(filter_frame, 
                                                 textvariable=self.filter_category_var,
                                                 width=15)
        self.filter_category_combo.grid(row=0, column=3, padx=5, sticky="w")
        
        # Кнопки фильтров
        ttk.Button(filter_frame, text="Применить", command=self.apply_filters,
                  width=10).grid(row=0, column=4, padx=(10, 5))
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters,
                  width=10).grid(row=0, column=5, padx=5)
        
        # Список операций
        list_frame = ttk.LabelFrame(self.root, text="Операции", padding=10)
        list_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        # Таблица
        columns = ("id", "date", "type", "category", "amount", "description")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Заголовки с сортировкой
        for col in columns:
            self.tree.heading(col, text=col.capitalize(), 
                             command=lambda c=col: self.sort_by(c))
            width = 50 if col == "id" else 100 if col == "date" else 80 if col == "type" else 120 if col == "category" else 100 if col == "amount" else 200
            self.tree.column(col, width=width, stretch=(col == "description"))
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Панель управления
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Кнопки управления
        buttons = [
            ("Обновить", self.refresh_all),
            ("Удалить", self.delete_selected),
            ("Баланс", self.show_balance),
            ("Экспорт CSV", lambda: self.export_data("csv")),
            ("Экспорт JSON", lambda: self.export_data("json")),
            ("Импорт", self.import_data),
        ]
        
        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(control_frame, text=text, command=cmd).grid(
                row=0, column=i, padx=2, sticky="ew")
            control_frame.columnconfigure(i, weight=1)
        
        # Панель анализа
        analysis_frame = ttk.LabelFrame(self.root, text="Анализ", padding=10)
        analysis_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky="nsew")
        
        # Кнопки анализа
        ttk.Button(analysis_frame, text="График доходов/расходов", 
                  command=self.plot_income_expense, width=20).pack(fill=tk.X, pady=5)
        ttk.Button(analysis_frame, text="Расходы по категориям", 
                  command=self.plot_categories, width=20).pack(fill=tk.X, pady=5)
        ttk.Button(analysis_frame, text="Топ расходов", 
                  command=self.plot_top_expenses, width=20).pack(fill=tk.X, pady=5)
        
        # Статистика
        stats_frame = ttk.LabelFrame(analysis_frame, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.balance_label = ttk.Label(stats_frame, text="Баланс: 0.00 руб")
        self.balance_label.pack(anchor="w", pady=2)
        
        self.count_label = ttk.Label(stats_frame, text="Операций: 0")
        self.count_label.pack(anchor="w", pady=2)
        
        # Настройка размеров
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
    
    def sort_by(self, column):
        """Сортировка по колонке"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.refresh_list()
    
    def apply_filters(self):
        """Применение фильтров"""
        self.current_filters = {}
        
        # Тип операции
        filter_type = self.filter_type_var.get()
        if filter_type != "все":
            self.current_filters['type'] = OperationType(filter_type)
        
        # Категория
        filter_category = self.filter_category_var.get()
        if filter_category != "все":
            self.current_filters['category'] = filter_category.strip()
        
        self.refresh_list()
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type_var.set("все")
        self.filter_category_var.set("все")
        self.current_filters = {}
        self.refresh_list()
    
    def get_filtered_operations(self):
        """Получение отфильтрованных операций"""
        return self.manager.get_filtered_operations(
            category=self.current_filters.get('category'),
            op_type=self.current_filters.get('type')
        )
    
    def refresh_list(self):
        """Обновление списка операций"""
        # Очистка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение и сортировка
        operations = self.get_filtered_operations()
        
        # Сортировка
        if self.sort_column == "id":
            operations.sort(key=lambda x: x.id, reverse=self.sort_reverse)
        elif self.sort_column == "date":
            operations.sort(key=lambda x: x.date, reverse=self.sort_reverse)
        elif self.sort_column == "type":
            operations.sort(key=lambda x: x.type.value, reverse=self.sort_reverse)
        elif self.sort_column == "category":
            operations.sort(key=lambda x: x.category, reverse=self.sort_reverse)
        elif self.sort_column == "amount":
            operations.sort(key=lambda x: x.amount, reverse=self.sort_reverse)
        elif self.sort_column == "description":
            operations.sort(key=lambda x: x.description, reverse=self.sort_reverse)
        
        # Добавление в таблицу
        for op in operations:
            self.tree.insert("", tk.END, values=(
                op.id,
                op.date,
                op.type.value,
                op.category,
                f"{op.amount:.2f}",
                op.description
            ))
    
    def refresh_all(self):
        """Полное обновление интерфейса"""
        # Обновление категорий в фильтре
        categories = ["все"] + self.manager.get_categories()
        self.filter_category_combo['values'] = categories
        
        # Обновление списка
        self.refresh_list()
        
        # Обновление статистики
        ops = self.get_filtered_operations()
        balance = self.manager.get_balance(ops)
        self.balance_label.config(text=f"Баланс: {balance:.2f} руб")
        self.count_label.config(text=f"Операций: {len(ops)}")
    
    def add_operation(self):
        """Добавление новой операции"""
        try:
            # Получение данных
            amount = float(self.amount_var.get())
            category = self.category_var.get()
            date = self.date_var.get()
            op_type = OperationType(self.type_var.get())
            description = self.description_var.get()
            
            # Проверка
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительной")
                return
            
            if not category.strip():
                messagebox.showerror("Ошибка", "Введите категорию")
                return
            
            # Добавление
            if self.manager.add_operation(amount, category, date, op_type, description):
                self.save_data()
                self.refresh_all()
                messagebox.showinfo("Успех", "Операция добавлена")
                
                # Очистка полей
                self.amount_var.set("")
                self.category_var.set("")
                self.description_var.set("")
            else:
                messagebox.showerror("Ошибка", "Неверные данные (проверьте дату)")
                
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def delete_selected(self):
        """Удаление выбранной операции"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите операцию")
            return
        
        item = selection[0]
        op_id = int(self.tree.item(item, "values")[0])
        
        if messagebox.askyesno("Подтверждение", "Удалить операцию?"):
            if self.manager.delete_operation(op_id):
                self.save_data()
                self.refresh_all()
                messagebox.showinfo("Успех", "Операция удалена")
    
    def show_balance(self):
        """Показ баланса"""
        ops = self.get_filtered_operations()
        balance = self.manager.get_balance(ops)
        total_income = sum(op.amount for op in ops if op.type == OperationType.INCOME)
        total_expense = sum(op.amount for op in ops if op.type == OperationType.EXPENSE)
        
        messagebox.showinfo("Баланс",
                          f"Баланс: {balance:.2f} руб\n"
                          f"Доходы: {total_income:.2f} руб\n"
                          f"Расходы: {total_expense:.2f} руб")
    
    def export_data(self, format_type):
        """Экспорт данных"""
        if format_type == "csv":
            filetypes = [("CSV files", "*.csv")]
            defaultext = ".csv"
        else:
            filetypes = [("JSON files", "*.json")]
            defaultext = ".json"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=defaultext,
            filetypes=filetypes
        )
        
        if filename:
            ops = self.get_filtered_operations()
            if format_type == "csv":
                success = self.storage.export_to_csv(ops, filename)
            else:
                success = self.storage.export_to_json(ops, filename)
            
            if success:
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать данные")
    
    def import_data(self):
        """Импорт данных."""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Все файлы", "*.*"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        
        if not filename:
            return
        
        try:
            # Определяем обработчик по расширению
            if filename.lower().endswith('.json'):
                imported = self.import_json_file(filename)  # Используем метод из DataStorage
            else:
                imported = self.storage.import_from_csv(filename)
            
            self.process_imported_data(imported, filename)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {e}")


    def import_json_file(self, filename):
        """Импорт JSON файла."""
        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported = []
            if isinstance(data, list):
                for item in data:
                    try:
                        imported.append({
                            'amount': float(item.get('amount', 0)),
                            'category': str(item.get('category', '')).strip(),
                            'date': str(item.get('date', '2024-01-01')).strip(),
                            'type': str(item.get('type', 'расход')).strip(),
                            'description': str(item.get('description', '')).strip(),
                            'id': int(item.get('id', 0))
                        })
                    except Exception:
                        continue
            return imported
        except Exception as e:
            print(f"JSON import error: {e}")
            return []

    def process_imported_data(self, imported, filename):
        """Обработка импортированных данных"""
        if not imported:
            messagebox.showerror("Ошибка", "Не удалось импортировать данные")
            return
        
        if not messagebox.askyesno("Подтверждение", f"Импортировать {len(imported)} записей?"):
            return
        
        count = 0
        for data in imported:
            try:
                if self.manager.add_operation(
                    float(data['amount']),
                    data['category'],
                    data['date'],
                    OperationType(data['type']),
                    data.get('description', '')
                ):
                    count += 1
            except Exception:
                continue
        
        if count > 0:
            self.save_data()
            self.refresh_all()
            messagebox.showinfo("Успех", f"Импортировано {count} записей")
        else:
            messagebox.showwarning("Внимание", "Не импортировано ни одной записи")
    def plot_income_expense(self):
        """Построение графика доходов/расходов"""
        try:
            fig = self.analyzer.plot_income_vs_expenses()
            self.show_plot(fig, "Доходы и расходы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график: {e}")

    def plot_categories(self):
        """Построение графика расходов по категориям"""
        try:
            fig = self.analyzer.plot_expenses_by_category()
            self.show_plot(fig, "Расходы по категориям")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график: {e}")

    def plot_top_expenses(self):
        """Построение графика топ расходов"""
        try:
            fig = self.analyzer.plot_top_expenses()
            self.show_plot(fig, "Топ расходов")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график: {e}")

    def show_plot(self, fig, title):
        """Отображение графика"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("800x600")
        
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(window, text="Закрыть", command=window.destroy).pack(pady=10)

    def run(self):
        """Запуск главного цикла"""
        self.root.mainloop()