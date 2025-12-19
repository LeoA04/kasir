import time
import random
from locust import task, SequentialTaskSet
from faker import Faker
from load_test_config import RESPONSE_TIME_SLO, TEST_USERS

fake = Faker('id_ID')

class SignupLoginFlow(SequentialTaskSet):
    """
    Sequential flow: Signup -> Login -> Logout
    Test complete authentication cycle
    """
    
    def on_start(self):
        self.test_username = f"testuser_{fake.random_int(min=1000, max=9999)}"
        self.test_password = f"pass{fake.random_int(min=100000, max=999999)}"
    
    @task
    def signup(self):
        start_time = time.time()
        
        with self.client.post(
            "/api/signup",
            json={
                "username": self.test_username,
                "password": self.test_password,
                "confirm_password": self.test_password
            },
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 201:
                if response_time > RESPONSE_TIME_SLO["normal"]:
                    response.failure(f"Signup slow: {response_time:.0f}ms > {RESPONSE_TIME_SLO['normal']}ms")
                else:
                    response.success()
            else:
                response.failure(f"Signup failed: {response.status_code}")
    
    @task
    def login(self):
        start_time = time.time()
        
        with self.client.post(
            "/api/login",
            json={
                "username": self.test_username,
                "password": self.test_password
            },
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Login slow: {response_time:.0f}ms > {RESPONSE_TIME_SLO['fast']}ms")
                else:
                    response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @task
    def logout(self):
        start_time = time.time()
        
        with self.client.get("/logout", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 302:  # Redirect
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Logout slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Logout failed: {response.status_code}")


class LoginWithDifferentRoles(SequentialTaskSet):
    """
    Test login dengan berbagai role (admin, kasir, user)
    Untuk test role-based access control performance
    """
    
    @task
    def login_as_admin(self):
        self._perform_login(TEST_USERS["admin"], "Admin")
    
    @task
    def login_as_kasir(self):
        kasir = random.choice([TEST_USERS["kasir1"], TEST_USERS["kasir2"]])
        self._perform_login(kasir, "Kasir")
    
    @task
    def login_as_user(self):
        self._perform_login(TEST_USERS["user1"], "User")
    
    def _perform_login(self, credentials, role_name):
        """Helper method untuk login"""
        start_time = time.time()
        
        with self.client.post(
            "/api/login",
            json={
                "username": credentials["username"],
                "password": credentials["password"]
            },
            catch_response=True,
            name=f"/api/login [as {role_name}]"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                expected_role = credentials["role"]
                actual_role = data.get("role")
                
                if actual_role != expected_role:
                    response.failure(f"Wrong role: expected {expected_role}, got {actual_role}")
                elif response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Login slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")


class ConcurrentLoginStressTest(SequentialTaskSet):
    """
    Stress test untuk concurrent login
    Simulasi banyak user login bersamaan (opening shift scenario)
    """
    
    @task(5)
    def rapid_login_attempts(self):
        # Simulasi 3 login attempts berturut-turut (typo password scenario)
        attempts = 3
        for i in range(attempts):
            credentials = random.choice(list(TEST_USERS.values()))
            
            # 70% correct password, 30% wrong password
            password = credentials["password"] if random.random() > 0.3 else "wrongpassword"
            
            start_time = time.time()
            with self.client.post(
                "/api/login",
                json={
                    "username": credentials["username"],
                    "password": password
                },
                catch_response=True,
                name=f"/api/login [attempt {i+1}]"
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if password == credentials["password"]:
                    if response.status_code == 200:
                        if response_time > RESPONSE_TIME_SLO["fast"]:
                            response.failure(f"Slow: {response_time:.0f}ms")
                        else:
                            response.success()
                            break
                    else:
                        response.failure("Login should succeed but failed")
                else:
                    if response.status_code == 401:
                        response.success()
                    else:
                        response.failure(f"Wrong status: {response.status_code}")
            
            time.sleep(0.1)