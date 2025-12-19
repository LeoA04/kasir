import time
import random
from locust import task, SequentialTaskSet
from load_test_config import RESPONSE_TIME_SLO, TEST_USERS, TEST_PROMOS

class CompleteShoppingJourney(SequentialTaskSet):
    def on_start(self):
        """Login sebelum mulai belanja"""
        self.client.post("/api/login", json={
            "username": "kasir1",
            "password": "kasir123"
        })
        self.product_ids = []
    
    @task
    def view_homepage(self):
        """Browse homepage dan lihat produk"""
        start_time = time.time()
        
        with self.client.get("/", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # Extract product IDs from response (jika HTML parsing diperlukan)
                # Untuk sekarang assume IDs 1-5
                self.product_ids = list(range(1, 6))
                
                if response_time > RESPONSE_TIME_SLO["normal"]:
                    response.failure(f"Homepage slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Homepage load failed: {response.status_code}")
    
    @task
    def add_multiple_items_to_cart(self):
        """Add 2-4 items to cart"""
        num_items = random.randint(2, 4)
        
        for _ in range(num_items):
            product_id = random.choice(self.product_ids) if self.product_ids else random.randint(1, 5)
            
            start_time = time.time()
            with self.client.post(
                "/api/cart/add",
                json={"product_id": product_id},
                catch_response=True
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    if response_time > RESPONSE_TIME_SLO["fast"]:
                        response.failure(f"Add to cart slow: {response_time:.0f}ms")
                    else:
                        response.success()
                elif response.status_code == 400:
                    # Stok habis - expected behavior
                    response.success()
                else:
                    response.failure(f"Add to cart failed: {response.status_code}")
            
            time.sleep(random.uniform(0.5, 2))  # Think time
    
    @task
    def view_cart(self):
        """Check cart contents"""
        start_time = time.time()
        
        with self.client.get("/api/cart", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.cart_total = data.get("total", 0)
                
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"View cart slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"View cart failed: {response.status_code}")
    
    @task
    def apply_promo_and_checkout(self):
        """Apply promo code (50% chance) and checkout"""
        # 50% menggunakan promo
        promo_code = random.choice(TEST_PROMOS)["code"] if random.random() > 0.5 else ""
        
        amount_paid = getattr(self, 'cart_total', 50000) + 10000
        
        start_time = time.time()
        with self.client.post(
            "/api/checkout",
            json={
                "amount_paid": amount_paid,
                "promo_code": promo_code
            },
            catch_response=True,
            name="/api/checkout [with promo]" if promo_code else "/api/checkout [no promo]"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "SUCCESS":
                    if response_time > RESPONSE_TIME_SLO["normal"]:
                        response.failure(f"Checkout slow: {response_time:.0f}ms")
                    else:
                        response.success()
                else:
                    response.failure("Checkout status not SUCCESS")
            elif response.status_code == 400:
                # Expected errors (empty cart, insufficient funds)
                response.success()
            else:
                response.failure(f"Checkout failed: {response.status_code}")
    
    @task
    def view_history(self):
        """View transaction history"""
        start_time = time.time()
        
        with self.client.get("/api/history", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                if response_time > RESPONSE_TIME_SLO["normal"]:
                    response.failure(f"History slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"History failed: {response.status_code}")


class CartManipulationStress(SequentialTaskSet):
    """
    Stress test untuk cart operations
    Add/reduce items dengan cepat untuk test concurrency
    """
    
    def on_start(self):
        """Setup"""
        self.client.post("/api/login", json={
            "username": "kasir2",
            "password": "kasir123"
        })
    
    @task(5)
    def rapid_add_to_cart(self):
        product_id = random.randint(1, 5)
        
        # Add same item 3-5 times rapidly
        for _ in range(random.randint(3, 5)):
            start_time = time.time()
            
            with self.client.post(
                "/api/cart/add",
                json={"product_id": product_id},
                catch_response=True,
                name="/api/cart/add [rapid]"
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code in [200, 400]:  # 400 = stok habis (OK)
                    if response_time > RESPONSE_TIME_SLO["fast"]:
                        response.failure(f"Slow: {response_time:.0f}ms")
                    else:
                        response.success()
                else:
                    response.failure(f"Unexpected status: {response.status_code}")
    
    @task(2)
    def rapid_reduce_from_cart(self):
        product_id = random.randint(1, 5)
        
        # Try to reduce 2-3 times
        for _ in range(random.randint(2, 3)):
            start_time = time.time()
            
            with self.client.post(
                "/api/cart/reduce",
                json={"product_id": product_id},
                catch_response=True,
                name="/api/cart/reduce [rapid]"
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code in [200, 404]:  # 404 = item not in cart (OK)
                    if response_time > RESPONSE_TIME_SLO["fast"]:
                        response.failure(f"Slow: {response_time:.0f}ms")
                    else:
                        response.success()
                else:
                    response.failure(f"Unexpected status: {response.status_code}")


class CheckoutWithVariousScenarios(SequentialTaskSet):
    """
    Test checkout dengan berbagai kondisi:
    - Insufficient funds
    - Empty cart
    - Valid checkout
    - With/without promo
    """
    
    def on_start(self):
        """Setup"""
        self.client.post("/api/login", json={
            "username": "user1",
            "password": "user123"
        })
    
    @task
    def checkout_empty_cart(self):
        """Test checkout dengan cart kosong (expected to fail)"""
        start_time = time.time()
        
        with self.client.post(
            "/api/checkout",
            json={"amount_paid": 100000, "promo_code": ""},
            catch_response=True,
            name="/api/checkout [empty cart]"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                # Expected failure
                if response_time > RESPONSE_TIME_SLO["fast"]:
                    response.failure(f"Error handling slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Should return 400, got {response.status_code}")
    
    @task
    def checkout_insufficient_funds(self):
        """Test checkout dengan uang tidak cukup"""
        # Add item dulu
        self.client.post("/api/cart/add", json={"product_id": 1})
        
        start_time = time.time()
        with self.client.post(
            "/api/checkout",
            json={"amount_paid": 100, "promo_code": ""},  # Uang sangat kurang
            catch_response=True,
            name="/api/checkout [insufficient funds]"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                if response_time > RESPONSE_TIME_SLO["normal"]:
                    response.failure(f"Slow: {response_time:.0f}ms")
                else:
                    response.success()
            else:
                response.failure(f"Should return 400")
    
    @task
    def valid_checkout_with_promo(self):
        """Test valid checkout dengan promo"""
        # Add items
        for _ in range(2):
            self.client.post("/api/cart/add", json={"product_id": random.randint(1, 5)})
        
        # Get cart total
        cart_response = self.client.get("/api/cart")
        if cart_response.status_code == 200:
            cart_total = cart_response.json().get("total", 50000)
            
            start_time = time.time()
            with self.client.post(
                "/api/checkout",
                json={
                    "amount_paid": cart_total + 50000,  # Overpay
                    "promo_code": "DISKON10"
                },
                catch_response=True,
                name="/api/checkout [valid with promo]"
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    if response_time > RESPONSE_TIME_SLO["normal"]:
                        response.failure(f"Slow: {response_time:.0f}ms")
                    else:
                        response.success()
                else:
                    response.failure(f"Checkout failed: {response.status_code}")