# Тесты 

import unittest
import os
import tempfile
from models import Operation, OperationType, FinanceManager
from storage import DataStorage

class TestModels(unittest.TestCase):
    """Тесты моделей"""
    
    def test_operation_validation(self):
        """Тест валидации операции"""
        op = Operation(1, 100.0, "Категория", "2024-01-01", OperationType.INCOME)
        self.assertTrue(op.validate())
        
        op = Operation(2, -100.0, "Категория", "2024-01-01", OperationType.INCOME)
        self.assertFalse(op.validate())
        
        op = Operation(3, 100.0, "Категория", "2024-13-01", OperationType.INCOME)
        self.assertFalse(op.validate())
    
    def test_finance_manager(self):
        """Тест менеджера операций"""
        manager = FinanceManager()
        
        # Добавление
        self.assertTrue(manager.add_operation(100.0, "Категория", "2024-01-01", 
                                            OperationType.INCOME, "Описание"))
        self.assertEqual(len(manager.operations), 1)
        
        # Удаление
        self.assertTrue(manager.delete_operation(1))
        self.assertEqual(len(manager.operations), 0)
        
        # Баланс
        manager.add_operation(200.0, "Доход", "2024-01-01", OperationType.INCOME)
        manager.add_operation(50.0, "Расход", "2024-01-02", OperationType.EXPENSE)
        self.assertEqual(manager.get_balance(), 150.0)

class TestStorage(unittest.TestCase):
    """Тесты хранилища"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.csv")
    
    def tearDown(self):
        """Очистка"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_load(self):
        """Тест сохранения и загрузки"""
        storage = DataStorage(self.test_file)
        
        # Тестовые операции
        from models import Operation, OperationType
        operations = [
            Operation(1, 100.0, "Категория1", "2024-01-01", OperationType.INCOME, "Описание1"),
            Operation(2, 50.0, "Категория2", "2024-01-02", OperationType.EXPENSE, "Описание2")
        ]
        
        # Сохранение
        self.assertTrue(storage.save_data(operations))
        self.assertTrue(os.path.exists(self.test_file))
        
        # Загрузка
        loaded, next_id = storage.load_data()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(next_id, 3)

if __name__ == '__main__':
    unittest.main()
