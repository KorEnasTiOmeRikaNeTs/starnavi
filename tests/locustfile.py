# tests/locustfile.py

import os

from locust import HttpUser, task, between
import random
import string
import jwt


# Функція для створення випадкових рядків
def random_string(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Функція для генерації JWT токена
def generate_token(user_id, username):
    payload = {"sub": username, "id": user_id}
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    return jwt.encode(payload, secret_key, algorithm=algorithm)


class PerfTestUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """
        Виконується перед початком тестування для кожного користувача.
        Створюємо тестового користувача та отримуємо токен.
        """
        self.username = random_string()
        self.email = f"{self.username}@example.com"
        self.password = "password123"

        # Реєстрація користувача
        response = self.client.post(
            "/auth/register",
            json={
                "username": self.username,
                "email": self.email,
                "password": self.password,
            },
        )

        if response.status_code == 201:
            self.user_id = response.json()["user_id"]
            self.token = generate_token(self.user_id, self.username)
        else:
            print("Error registering user")
            self.user_id = None
            self.token = None

    @task(2)
    def create_post(self):
        """
        Тест створення поста.
        """
        if self.token:
            post_data = {
                "title": f"Post {random_string(5)}",
                "content": "This is a performance test post.",
            }
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.post("/posts/create-post", json=post_data, headers=headers)

    @task(1)
    def create_comment(self):
        """
        Тест створення коментаря.
        """
        if self.token:
            comment_data = {"content": f"This is a test comment {random_string(5)}"}
            headers = {"Authorization": f"Bearer {self.token}"}
            # Припускаємо, що пост із ID 1 існує
            self.client.post("/comments/create/1", json=comment_data, headers=headers)

    @task(1)
    def check_autoreply_status(self):
        """
        Тест перевірки статусу автоматичної відповіді.
        """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/user/profile-page", headers=headers)
