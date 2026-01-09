# Хранение данных (CSV/JSON)

import csv
import json
import os
from typing import List, Dict, Any
from models import Operation, OperationType

class DataStorage:
    """Хранилище данных"""
    
    def __init__(self, data_file: str = "data.csv"):
        """Инициализация хранилища"""
        self.data_file = data_file
    
    def load_data(self) -> tuple[List[Operation], int]:
        """Загрузка данных из CSV файла"""
        operations = []
        
        if not os.path.exists(self.data_file):
            return operations, 1
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        operation = Operation(
                            id=int(row['id']),
                            amount=float(row['amount']),
                            category=row['category'].strip(),
                            date=row['date'],
                            type=OperationType(row['type']),
                            description=row.get('description', '').strip()
                        )
                        operations.append(operation)
                    except (ValueError, KeyError):
                        continue
                        
            next_id = max([op.id for op in operations], default=0) + 1
            return operations, next_id
            
        except Exception:
            return [], 1
    
    def save_data(self, operations: List[Operation]) -> bool:
        """Сохранение данных в CSV файл"""
        try:
            with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'amount', 'category', 'date', 'type', 'description'])
                for op in operations:
                    writer.writerow([
                        op.id,
                        op.amount,
                        op.category,
                        op.date,
                        op.type.value,
                        op.description
                    ])
            return True
        except Exception:
            return False
    
    def export_to_csv(self, operations: List[Operation], filename: str) -> bool:
        """Экспорт данных в CSV файл"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'amount', 'category', 'date', 'type', 'description'])
                for op in operations:
                    writer.writerow([
                        op.id,
                        op.amount,
                        op.category,
                        op.date,
                        op.type.value,
                        op.description
                    ])
            return True
        except Exception:
            return False
    
    def export_to_json(self, operations: List[Operation], filename: str) -> bool:
        """Экспорт данных в JSON файл"""
        try:
            data = []
            for op in operations:
                data.append({
                    'id': op.id,
                    'amount': op.amount,
                    'category': op.category,
                    'date': op.date,
                    'type': op.type.value,
                    'description': op.description
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def import_from_csv(self, filename: str) -> List[Dict[str, Any]]:
        """Импорт данных из CSV файла"""
        imported = []
        
        if not os.path.exists(filename):
            return imported
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Очистка данных
                        clean_category = row['category'].strip()
                        clean_description = row.get('description', '').strip()
                        
                        imported.append({
                            'amount': float(row['amount']),
                            'category': clean_category,
                            'date': row['date'].strip(),
                            'type': row.get('type', 'расход').strip(),
                            'description': clean_description,
                            'id': int(row.get('id', 0))
                        })
                    except (ValueError, KeyError):
                        continue
                        
            return imported
            
        except Exception:
            return []
        
    def import_json_file(self, filename):
        """Импорт данных из JSON файла"""
        imported = []
    
        if not os.path.exists(filename):
            return imported
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    try:
                        imported.append({
                            'amount': float(item['amount']),
                            'category': str(item.get('category', '')).strip(),
                            'date': str(item.get('date', '2024-01-01')).strip(),
                            'type': str(item.get('type', 'расход')).strip(),
                            'description': str(item.get('description', '')).strip(),
                            'id': int(item.get('id', 0))
                        })
                    except (ValueError, KeyError):
                        continue
            
            return imported
            
        except Exception as e:
            print(f"Ошибка импорта JSON: {e}")
            return []