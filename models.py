# Модели данных

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

class OperationType(Enum):
    """Тип операции: доход или расход"""
    INCOME = "доход"
    EXPENSE = "расход"

@dataclass
class Operation:
    """Финансовая операция"""
    id: int
    amount: float
    category: str
    date: str
    type: OperationType
    description: str = ""
    
    def validate(self) -> bool:
        """Валидация данных операции"""
        # Валидация суммы
        if self.amount <= 0:
            return False
        
        # Валидация даты (регулярное выражение)
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, self.date):
            return False
        
        try:
            datetime.strptime(self.date, '%Y-%m-%d')
        except ValueError:
            return False
        
        return True

class FinanceManager:
    """Менеджер финансовых операций"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.operations: List[Operation] = []
        self.next_id = 1
    
    def add_operation(self, amount: float, category: str, date: str, 
                     operation_type: OperationType, description: str = "") -> bool:
        """Добавление новой операции"""
        try:
            # Очистка данных
            clean_category = category.strip()
            clean_description = description.strip()
            
            operation = Operation(
                id=self.next_id,
                amount=amount,
                category=clean_category,
                date=date,
                type=operation_type,
                description=clean_description
            )
            
            if not operation.validate():
                return False
            
            self.operations.append(operation)
            self.next_id += 1
            return True
            
        except Exception:
            return False
    
    def delete_operation(self, operation_id: int) -> bool:
        """Удаление операции"""
        for i, op in enumerate(self.operations):
            if op.id == operation_id:
                self.operations.pop(i)
                return True
        return False
    
    def get_filtered_operations(self, 
                               category: Optional[str] = None,
                               op_type: Optional[OperationType] = None,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> List[Operation]:
        """Получение отфильтрованного списка операций"""
        filtered = self.operations.copy()
        
        if category:
            clean_category = category.strip()
            filtered = [op for op in filtered if op.category == clean_category]
        
        if op_type:
            filtered = [op for op in filtered if op.type == op_type]
        
        if start_date:
            filtered = [op for op in filtered if op.date >= start_date]
        
        if end_date:
            filtered = [op for op in filtered if op.date <= end_date]
        
        return filtered
    
    def get_balance(self, filtered_ops: Optional[List[Operation]] = None) -> float:
        """Расчет баланса"""
        ops = filtered_ops if filtered_ops else self.operations
        balance = 0.0
        for op in ops:
            if op.type == OperationType.INCOME:balance += op.amount
            else:
                balance -= op.amount
        return balance
    
    def get_categories(self) -> List[str]:
        """Получение списка уникальных категорий"""
        return sorted(set(op.category for op in self.operations))