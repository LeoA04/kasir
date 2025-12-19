import time
import random
from locust import task, TaskSet, between
from load_test_config import RESPONSE_TIME_SLO

class RealisticPOSWorkload(TaskSet):
    """
    Realistic mixed workload:
    - Multiple kasir melayani customer
    - Admin occasionally manages inventory
    - Various transaction patterns
    """
    
    wait_time = between(1, 3)  # Realistic think time
    
    def on_start(self):
        """Login sebagai kasir atau admin (weighted)"""
        # 80% kasir, 20% admin
        if random.random() < 0.8:
            self.role = "kasir"
            self.username = random.choice(["kasir1", "kasir2"])
            self.password = "kasir123"
        else:
            self.role = "admin"
            self.username = "admin"
            self.password = "admin123"
        
        self.client.post("/api/login", json={
            "username": self.username,
            "password": self.password
        })
    
    @task(10)
    def serve_customer_quick_transaction(self):
        if self.role != "kasir":
            return
        
        # Add 1-2 items
        for _ in range(random.randint(1, 2)):
            self.client.post("/api/cart/add", json={
                "product_id": random.randint(1, 5)
            })
            time.sleep(random.uniform(0.2, 0.5))
        
        # Quick checkout
        cart_response = self.client.get("/api/cart")
        if cart_response.status_code == 200:
            total = cart_response.json().get("total", 20000)
            
            self.client.post("/api/checkout", json={
                "amount_paid": total + random.randint(0, 50000),
                "promo_code": ""
            })
    
    @task(5)
    def serve_customer_medium_transaction(self):
        if self.role != "kasir":
            return
        
        # Add 3-5 items
        for _ in range(random.randint(3, 5)):
            self.client.post("/api/cart/add", json={
                "product_id": random.randint(1, 5)
            })
            time.sleep(random.uniform(0.5, 1))
        
        # Maybe adjust cart
        if random.random() < 0.3:
            self.client.post("/api/cart/reduce", json={
                "product_id": random.randint(1, 5)
            })
        
        # Checkout with possible promo
        cart_response = self.client.get("/api/cart")
        if cart_response.status_code == 200:
            total = cart_response.json().get("total", 50000)
            promo = random.choice(["", "DISKON10", "HEMAT20"])
            
            self.client.post("/api/checkout", json={
                "amount_paid": total + random.randint(0, 100000),
                "promo_code": promo
            })
    
    @task(2)
    def serve_customer_large_transaction(self):
        if self.role != "kasir":
            return
        
        # Add 6-10 items with some duplicates
        for _ in range(random.randint(6, 10)):
            self.client.post("/api/cart/add", json={
                "product_id": random.randint(1, 5)
            })
            time.sleep(random.uniform(0.3, 0.7))
        
        # Multiple cart adjustments
        for _ in range(random.randint(1, 3)):
            if random.random() < 0.5:
                self.client.post("/api/cart/add", json={
                    "product_id": random.randint(1, 5)
                })
            else:
                self.client.post("/api/cart/reduce", json={
                    "product_id": random.randint(1, 5)
                })
            time.sleep(0.5)
        
        # Checkout with promo
        cart_response = self.client.get("/api/cart")
        if cart_response.status_code == 200:
            total = cart_response.json().get("total", 100000)
            promo = random.choice(["DISKON10", "HEMAT20", "PROMO50"])
            
            self.client.post("/api/checkout", json={
                "amount_paid": total + random.randint(0, 150000),
                "promo_code": promo
            })
    
    @task(3)
    def check_transaction_history(self):
        if self.role != "kasir":
            return
        
        self.client.get("/api/history")
    
    @task(1)
    def admin_check_dashboard(self):
        if self.role != "admin":
            return
        
        self.client.get("/admin")
    
    @task(1)
    def admin_update_inventory(self):
        if self.role != "admin":
            return
        
        product_id = random.randint(1, 5)
        new_stock = random.randint(50, 150)
        
        self.client.post("/api/admin/update_stock", json={
            "id": product_id,
            "new_stock": new_stock
        })


class RushHourSimulation(TaskSet):
    """
    Simulate rush hour (jam sibuk)
    - Banyak transaksi bersamaan
    - Minimal think time
    - High concurrency
    """
    
    wait_time = between(0.1, 0.5)  # Minimal wait time (rush!)
    
    def on_start(self):
        """Login cepat"""
        self.client.post("/api/login", json={
            "username": random.choice(["kasir1", "kasir2"]),
            "password": "kasir123"
        })
    
    @task(20)
    def rush_transaction(self):
        # Quick add 1-3 items
        items = random.randint(1, 3)
        for _ in range(items):
            self.client.post("/api/cart/add", json={
                "product_id": random.randint(1, 5)
            })
        
        # Quick checkout
        cart = self.client.get("/api/cart").json()
        total = cart.get("total", 30000)
        
        self.client.post("/api/checkout", json={
            "amount_paid": total + 20000,
            "promo_code": ""
        })


class EnduranceTestingFlow(TaskSet):
    """
    Long-running flow untuk endurance testing
    Simulate store opening for full day
    """
    
    wait_time = between(2, 5)  # Normal think time
    
    def on_start(self):
        """Setup for long session"""
        self.client.post("/api/login", json={
            "username": "kasir1",
            "password": "kasir123"
        })
        self.transaction_count = 0
    
    @task(10)
    def regular_transaction(self):
        # Normal shopping flow
        items = random.randint(1, 4)
        for _ in range(items):
            self.client.post("/api/cart/add", json={
                "product_id": random.randint(1, 5)
            })
            time.sleep(random.uniform(0.5, 1.5))
        
        cart = self.client.get("/api/cart").json()
        total = cart.get("total", 40000)
        
        result = self.client.post("/api/checkout", json={
            "amount_paid": total + 30000,
            "promo_code": random.choice(["", "DISKON10"])
        })
        
        if result.status_code == 200:
            self.transaction_count += 1
    
    @task(2)
    def periodic_history_check(self):
        self.client.get("/api/history")
        
        # Log transaction count for monitoring
        if self.transaction_count % 10 == 0 and self.transaction_count > 0:
            print(f"[Endurance] User completed {self.transaction_count} transactions")


class StockDepletionScenario(TaskSet):
    wait_time = between(0.5, 1)
    
    def on_start(self):
        self.client.post("/api/login", json={
            "username": random.choice(["kasir1", "kasir2"]),
            "password": "kasir123"
        })
    
    @task(20)
    def try_buy_popular_product(self):
        # Try to add product 1 multiple times
        for _ in range(random.randint(2, 5)):
            start_time = time.time()
            
            with self.client.post(
                "/api/cart/add",
                json={"product_id": 1},  # Everyone wants product 1
                catch_response=True,
                name="/api/cart/add [popular item]"
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    # Success
                    if response_time > RESPONSE_TIME_SLO["fast"]:
                        response.failure(f"Slow: {response_time:.0f}ms")
                    else:
                        response.success()
                elif response.status_code == 400:
                    # Stock out - expected
                    response.success()
                else:
                    response.failure(f"Unexpected: {response.status_code}")
        
        # Try to checkout whatever in cart
        cart = self.client.get("/api/cart").json()
        if cart.get("items"):
            total = cart.get("total", 0)
            self.client.post("/api/checkout", json={
                "amount_paid": total + 50000,
                "promo_code": ""
            })


class PromoCodeAbuseTesting(TaskSet):
    wait_time = between(0.2, 0.8)
    
    def on_start(self):
        """Login"""
        self.client.post("/api/login", json={
            "username": random.choice(["kasir1", "kasir2"]),
            "password": "kasir123"
        })
    
    @task(15)
    def use_promo_code(self):
        # Add items
        for _ in range(random.randint(2, 4)):
            self.client.post("/api/cart/add", json={
                "product_id": random.randint(1, 5)
            })
        
        # Everyone uses same popular promo
        cart = self.client.get("/api/cart").json()
        total = cart.get("total", 50000)
        
        popular_promo = random.choice(["PROMO50", "HEMAT20", "DISKON10"])
        
        start_time = time.time()
        with self.client.post(
            "/api/checkout",
            json={
                "amount_paid": total + 20000,
                "promo_code": popular_promo
            },
            catch_response=True,
            name=f"/api/checkout [promo: {popular_promo}]"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["normal"]:
                    response.failure(f"Slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Checkout failed: {response.status_code}")