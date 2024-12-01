import unittest
from unittest.mock import patch, MagicMock
import main


class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        """Инициализация тестового объекта."""
        self.visualizer = main.DependencyVisualizer()
        self.visualizer.packsAndDeps = {
            "packageA": ["packageB", "packageC>=1.0"],
            "packageB": ["packageD"],
            "packageC": [],
            "packageD": [],
        }
        self.visualizer.packsByProvided = {
            "providedB": "packageB"
        }

    @patch('requests.get')
    @patch('tarfile.open')
    def test_start(self, mock_tarfile_open, mock_requests_get):
        """Тест загрузки и парсинга данных из APKINDEX."""
        mock_response = MagicMock()
        mock_response.content = b'fake content'
        mock_requests_get.return_value = mock_response

        mock_tarfile_instance = MagicMock()
        mock_tarfile_open.return_value.__enter__.return_value = mock_tarfile_instance
        mock_tarfile_instance.extractfile.return_value = MagicMock()

        self.visualizer.start()

        # Проверяем, что вызовы прошли
        mock_requests_get.assert_called_once()
        mock_tarfile_open.assert_called_once()

    def test_addDepends(self):
        """Тест рекурсивного добавления зависимостей."""
        self.visualizer.result = ""
        self.visualizer.setOfPacks = set()
        self.visualizer.addDepends("packageA")

        expected_result = "packageA --> packageB\npackageA --> packageC\npackageB --> packageD\n"
        self.assertEqual(self.visualizer.result, expected_result)

    def test_get_graph(self):
        """Тест генерации строки графа зависимостей."""
        self.visualizer.result = ""
        self.visualizer.addDepends("packageA")  # Заполняем зависимости
        graph_string = self.visualizer.get_graph("packageA")

        expected_graph_prefix = "graph\n"
        self.assertTrue(graph_string.startswith(expected_graph_prefix))
        self.assertIn("packageA --> packageB", graph_string)
        self.assertIn("packageA --> packageC", graph_string)
        self.assertIn("packageB --> packageD", graph_string)

    @patch('requests.get')
    def test_save_graph_to_png(self, mock_requests_get):
        """Тест сохранения графа в PNG файл."""
        graph_string = "graph\npackageA --> packageB\n"

        # Настройка мока для ответа на запрос изображения
        mock_response = MagicMock()
        mock_response.content = b'image data'
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        output_file_path = "output.png"

        # Сохраняем граф в PNG файл
        self.visualizer.save_graph_to_png(graph_string, output_file_path)

        # Проверяем, что изображение скачивается
        mock_requests_get.assert_called_once()

        # Проверяем, что файл был сохранен (проверка на открытие файла)
        with open(output_file_path, 'rb') as f:
            content = f.read()
            self.assertEqual(content, b'image data')


if __name__ == "__main__":
    unittest.main()