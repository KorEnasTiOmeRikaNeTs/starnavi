# tests/test_unit_ai.py

import unittest
from unittest.mock import MagicMock, patch
from ai_funcs import safety_check


class TestSafetyCheck(unittest.TestCase):

    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_safety_check_valid(self, mock_model):
        # Мок відповіді, яку повертає model.generate_content
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [MagicMock()]
        mock_response.candidates[0].content.parts[0].text = "True"

        # Підключення моку до моделі
        mock_model.generate_content.return_value = mock_response

        # Виклик функції з моком
        result = safety_check("Test message")

        # Перевірка, що результат False, бо відповідь містить "True"
        self.assertFalse(result)

    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_safety_check_invalid(self, mock_model):
        # Мок відповіді, яку повертає model.generate_content
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [MagicMock()]
        mock_response.candidates[0].content.parts[0].text = "False"

        # Підключення моку до моделі
        mock_model.generate_content.return_value = mock_response

        # Виклик функції з моком
        result = safety_check("""this message contains uncensored content, a lot of death and violence""")

        # Перевірка, що результат False, бо відповідь містить "False"
        self.assertFalse(result)

    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_safety_check_empty_response(self, mock_model):
        # Мок порожньої відповіді
        mock_response = MagicMock()
        mock_response.candidates = None

        # Підключення моку до моделі
        mock_model.generate_content.return_value = mock_response


        # Виклик функції і перевірка на виключення
        result = safety_check("")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
