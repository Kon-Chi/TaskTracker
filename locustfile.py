from locust import HttpUser, task


class User(HttpUser):
    @task
    def get(self):
        self.client.get(f"/tasks")
