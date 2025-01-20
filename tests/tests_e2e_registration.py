# tests/tests_e_to_e.py

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import faker
import allure
import json
import time

@pytest.fixture(scope="function")
def driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

class TestRegistration:
    @allure.story("Registration Flow")
    def test_successful_registration(self, driver):
        fake = faker.Faker()
        test_data = {
            "email": fake.email(),
            "password": "Test123!@#",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": fake.user_name()
        }
        
        try:
            # Відкриваємо Swagger UI
            with allure.step("Відкриваємо Swagger UI"):
                driver.get("http://localhost:8000/docs")
                time.sleep(3)  # Збільшуємо час очікування
                
            # Знаходимо і розгортаємо секцію auth
            with allure.step("Відкриваємо секцію auth"):
                # Оновлений селектор для auth секції
                auth_section = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'opblock-tag-section')]//h3[contains(text(), 'auth')]"))
                )
                auth_section.click()
                time.sleep(1)
                
            # Знаходимо POST /auth/register endpoint
            with allure.step("Відкриваємо POST /auth/register endpoint"):
                # Оновлений селектор для POST endpoint
                register_endpoint = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'opblock-summary-path') and contains(text(), '/auth/register')]//ancestor::div[contains(@class, 'opblock-post')]"))
                )
                register_endpoint.click()
                time.sleep(1)
                
            # Натискаємо Try it out
            with allure.step("Натискаємо Try it out"):
                try_it_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Try it out')]"))
                )
                try_it_button.click()
                time.sleep(1)
                
            # Заповнюємо тіло запиту
            with allure.step("Заповнюємо дані користувача"):
                request_body = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.body-param textarea"))
                )
                request_body.clear()
                request_body.send_keys(json.dumps(test_data, indent=2))
                
            # Виконуємо запит
            with allure.step("Виконуємо запит"):
                execute_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Execute')]"))
                )
                execute_button.click()
                time.sleep(2)
                
            # Перевіряємо результат
            with allure.step("Перевіряємо результат"):
                # Чекаємо на відповідь
                response_code = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.responses-table td.response-col_status"))
                )
                
                # Перевіряємо код відповіді
                assert "201" in response_code.text, f"Неочікуваний код відповіді: {response_code.text}"
                
                # Перевіряємо тіло відповіді
                response_body = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.highlight-code pre"))
                )
                
                response_json = json.loads(response_body.text)
                assert response_json["email"] == test_data["email"]
                assert response_json["username"] == test_data["username"]
                
            # Зберігаємо скріншот успішного виконання
            allure.attach(
                driver.get_screenshot_as_png(),
                name="successful_registration",
                attachment_type=allure.attachment_type.PNG
            )
                
        except Exception as e:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="error_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
            raise e

if __name__ == "__main__":
    pytest.main(["-v", "test_e2e_registration.py"])