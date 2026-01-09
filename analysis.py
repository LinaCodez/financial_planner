# Анализ и визуализация данных

import pandas as pd
import matplotlib.pyplot as plt
from models import OperationType

class DataAnalyzer:
    """Анализатор финансовых данных"""
    
    def __init__(self, finance_manager):
        """Инициализация анализатора"""
        self.manager = finance_manager
    
    def get_dataframe(self):
        """Преобразование операций в DataFrame"""
        data = []
        for op in self.manager.operations:
            data.append({
                'id': op.id,
                'amount': op.amount,
                'category': op.category,
                'date': pd.to_datetime(op.date),
                'type': op.type.value,
                'description': op.description
            })
        
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def plot_income_vs_expenses(self):
        """График доходов и расходов по месяцам"""
        df = self.get_dataframe()
        if df.empty:
            return self.create_empty_plot("Нет данных")
        
        # Группировка по месяцам
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        monthly.plot(kind='bar', ax=ax)
        ax.set_title('Доходы и расходы по месяцам')
        ax.set_xlabel('Месяц')
        ax.set_ylabel('Сумма (руб)')
        ax.legend(['Доходы', 'Расходы'])
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_expenses_by_category(self):
        """Круговая диаграмма расходов по категориям"""
        df = self.get_dataframe()
        if df.empty:
            return self.create_empty_plot("Нет данных")
        
        # Фильтрация расходов
        expenses = df[df['type'] == OperationType.EXPENSE.value]
        if expenses.empty:
            return self.create_empty_plot("Нет расходов")
        
        # Группировка по категориям
        by_category = expenses.groupby('category')['amount'].sum()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Круговая диаграмма
        ax1.pie(by_category.values, labels=by_category.index, autopct='%1.1f%%')
        ax1.set_title('Расходы по категориям')
        # Столбчатая диаграмма
        by_category.sort_values().plot(kind='barh', ax=ax2)
        ax2.set_title('Суммы по категориям')
        ax2.set_xlabel('Сумма (руб)')
        
        plt.tight_layout()
        return fig
    
    def plot_top_expenses(self, n=10):
        """Топ-N расходов"""
        df = self.get_dataframe()
        if df.empty:
            return self.create_empty_plot("Нет данных")
        
        # Фильтрация расходов
        expenses = df[df['type'] == OperationType.EXPENSE.value]
        if expenses.empty:
            return self.create_empty_plot("Нет расходов")
        
        # Топ-N расходов
        top_expenses = expenses.nlargest(n, 'amount')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(range(len(top_expenses)), top_expenses['amount'])
        
        # Подписи
        labels = [f"{row['category']} ({row['date'].strftime('%d.%m')})" 
                 for _, row in top_expenses.iterrows()]
        
        ax.set_yticks(range(len(top_expenses)))
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_title(f'Топ-{n} расходов')
        ax.set_xlabel('Сумма (руб)')
        
        # Значения на столбцах
        for bar, amount in zip(bars, top_expenses['amount']):
            ax.text(bar.get_width() + max(top_expenses['amount']) * 0.01,
                   bar.get_y() + bar.get_height()/2,
                   f'{amount:.0f}', va='center')
        
        plt.tight_layout()
        return fig
    
    def create_empty_plot(self, message):
        """Создание пустого графика с сообщением"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=14)
        ax.set_title('Нет данных для отображения')
        return fig
