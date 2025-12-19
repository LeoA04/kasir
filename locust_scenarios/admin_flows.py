import time
import random
from locust import task, SequentialTaskSet
from faker import Faker
from load_test_config import RESPONSE_TIME_SLO, TEST_PRODUCTS, TEST_PROMOS

fake = Faker('id_ID')

class AdminProductManagement(SequentialTaskSet):
    def on_start(self):
        """Login sebagai admin"""
        self.client.post("/api/login", json={
            "username": "admin",
            "password": "admin123"
        })
        self.created_product_ids = []
    
    @task
    def add_new_product(self):
        product = {
            "name": f"{fake.word().title()} {fake.word().title()}",
            "price": random.randint(5000, 50000),
            "stock": random.randint(10, 100),
            "category": random.choice(["makanan", "minuman"]),
            "img": random.choice(["☕", "🍵", "🍛", "🍜", "🍞", "🍕"])
        }
        
        start_time = time.time()
        with self.client.post(
            "/api/admin/add_product",
            json=product,
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["normal"]:
                    response.failure(f"Add product slow: {response_time:.0f}ms")
                else:
                    response.success()
            elif response.status_code == 403:
                response.failure("Unauthorized - session issue")
            else:
                response.failure(f"Add product failed: {response.status_code}")
    
    @task
    def update_product_stock(self):
        product_id = random.randint(1, 10)  # Assume products 1-10 exist
        new_stock = random.randint(0, 200)
        
        start_time = time.time()
        with self.client.post(
            "/api/admin/update_stock",
            json={"id": product_id, "new_stock": new_stock},
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Update stock slow: {response_time:.0f}ms")
                else:
                    response.success()
            elif response.status_code == 400:
                # Validation error (e.g., negative stock)
                response.success()  # Expected
            else:
                response.failure(f"Update stock failed: {response.status_code}")
    
    @task
    def delete_product(self):
        product_id = random.randint(6, 15)  # Random product
        
        start_time = time.time()
        with self.client.post(
            "/api/admin/delete_product",
            json={"id": product_id},
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [200, 404]:  # 404 = already deleted (OK)
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Delete product slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Delete product failed: {response.status_code}")
    
    @task
    def view_admin_dashboard(self):
        """Test load admin dashboard"""
        start_time = time.time()
        
        with self.client.get("/admin", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["slow"]:
                    response.failure(f"Dashboard very slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Dashboard load failed: {response.status_code}")


class AdminPromoManagement(SequentialTaskSet):
    def on_start(self):
        """Login sebagai admin"""
        self.client.post("/api/login", json={
            "username": "admin",
            "password": "admin123"
        })
    
    @task
    def add_new_promo(self):
        promo = {
            "code": f"PROMO{random.randint(1000, 9999)}",
            "discount_percent": random.choice([5, 10, 15, 20, 25, 30, 50])
        }
        
        start_time = time.time()
        with self.client.post(
            "/api/admin/add_promo",
            json=promo,
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Add promo slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Add promo failed: {response.status_code}")
    
    @task
    def delete_promo(self):
        promo_id = random.randint(1, 10)
        
        start_time = time.time()
        with self.client.post(
            "/api/admin/delete_promo",
            json={"id": promo_id},
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [200, 404]:
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Delete promo slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Delete promo failed: {response.status_code}")
    
    @task
    def get_promo_list(self):
        start_time = time.time()
        
        with self.client.get("/api/promos", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Get promos slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Get promos failed: {response.status_code}")


class AdminRoleManagement(SequentialTaskSet):
    def on_start(self):
        """Login sebagai admin"""
        self.client.post("/api/login", json={
            "username": "admin",
            "password": "admin123"
        })
    
    @task
    def view_role_management_page(self):
        """Test load role management page"""
        start_time = time.time()
        
        with self.client.get("/roles", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["normal"]:
                    response.failure(f"Role page slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Role page failed: {response.status_code}")
    
    @task
    def change_user_role(self):
        user_id = random.randint(2, 5)  # Assume users 2-5 exist
        new_role = random.choice(["user", "kasir", "admin"])
        
        start_time = time.time()
        with self.client.post(
            "/api/admin/set_role",
            json={"user_id": user_id, "role": new_role},
            catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Set role slow: {response_time:.0f}ms")
                else:
                    response.success()
            elif response.status_code == 404:
                response.success()  # User not found (acceptable)
            else:
                response.failure(f"Set role failed: {response.status_code}")


class AdminReportViewing(SequentialTaskSet):
    """
    Test performa viewing reports dan dashboard admin
    """
    
    def on_start(self):
        """Login sebagai admin"""
        self.client.post("/api/login", json={
            "username": "admin",
            "password": "admin123"
        })
    
    @task(3)
    def view_admin_dashboard_with_reports(self):
        """Test load dashboard dengan laporan hari ini"""
        start_time = time.time()
        
        with self.client.get("/admin", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # Dashboard dengan banyak data bisa lambat
                if response_time > RESPONSE_TIME_SLO["slow"]:
                    response.failure(f"Dashboard very slow: {response_time:.0f}ms")
                elif response_time > RESPONSE_TIME_SLO["normal"]:
                    # Warning tapi tidak fail
                    print(f"Warning: Dashboard slower than normal: {response_time:.0f}ms")
                    response.success()
                else:
                    response.success()
            else:
                response.failure(f"Dashboard failed: {response.status_code}")
    
    @task(1)
    def concurrent_admin_operations(self):
        # Simulate admin doing multiple things at once
        operations = [
            ("GET", "/admin", {}),
            ("GET", "/roles", {}),
            ("GET", "/api/promos", {}),
        ]
        
        for method, url, _ in operations:
            start_time = time.time()
            
            if method == "GET":
                response = self.client.get(url, catch_response=True)
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["slow"]:
                    response.failure(f"{url} very slow: {response_time:.0f}ms")
                else:
                    response.success()
            
            time.sleep(0.1)