"""
Smart POS Performance Testing - Main Locust File
================================================

Usage Examples:
--------------
1. Basic Load Test (Web UI):
   locust

2. Headless Load Test:
   locust --headless -u 50 -r 5 -t 5m

3. Specific Test Scenario:
   locust -f locustfile.py RealisticShoppingUser --headless -u 20 -r 2 -t 3m

4. Stress Test:
   locust -f locustfile.py StressTestUser --headless -u 200 -r 20 -t 10m

5. Master/Worker (Terminal 1 - Master):
   locust --master

6. Master/Worker (Terminal 2+ - Workers):
   locust --worker

Test Types Available:
--------------------
- RealisticShoppingUser: Simulasi user belanja normal
- StressTestUser: Stress testing dengan beban tinggi
- AdminUser: Admin operations testing
- MixedWorkloadUser: Kombinasi berbagai workflow
- RushHourUser: Simulasi jam sibuk
- EnduranceTestUser: Long-running test
"""

from locust import HttpUser, between, task
from locust_scenarios.auth_flows import (
    SignupLoginFlow,
    LoginWithDifferentRoles,
    ConcurrentLoginStressTest
)
from locust_scenarios.shopping_flows import (
    CompleteShoppingJourney,
    CartManipulationStress,
    CheckoutWithVariousScenarios
)
from locust_scenarios.admin_flows import (
    AdminProductManagement,
    AdminPromoManagement,
    AdminRoleManagement,
    AdminReportViewing
)
from locust_scenarios.mixed_flows import (
    RealisticPOSWorkload,
    RushHourSimulation,
    EnduranceTestingFlow,
    StockDepletionScenario,
    PromoCodeAbuseTesting
)
from load_test_config import BASE_URL


class RealisticShoppingUser(HttpUser):
    """
    Simulasi user/kasir yang melakukan transaksi normal
    - Browse produk
    - Add to cart
    - Checkout dengan/tanpa promo
    - View history
    
    Weight: 60% dari total users
    """
    host = BASE_URL
    wait_time = between(2, 5)  # Realistic think time
    weight = 60  # 60% of users
    
    tasks = {
        CompleteShoppingJourney: 10,
        CheckoutWithVariousScenarios: 3,
    }


class StressTestUser(HttpUser):
    """
    User untuk stress testing
    - Minimal wait time
    - Rapid operations
    - High concurrency scenarios
    """
    host = BASE_URL
    wait_time = between(0, 0.5)  # Minimal delay
    weight = 20
    
    tasks = {
        CartManipulationStress: 10,
        ConcurrentLoginStressTest: 5,
        StockDepletionScenario: 3,
    }


class AdminUser(HttpUser):
    """
    Simulasi admin operations
    - Product CRUD
    - Promo management
    - Reports viewing
    - Role management
    
    Weight: 5% dari total users (admin jarang)
    """
    host = BASE_URL
    wait_time = between(3, 8)  # Admin lebih lama mikir
    weight = 5
    
    tasks = {
        AdminProductManagement: 5,
        AdminPromoManagement: 3,
        AdminReportViewing: 10,
        AdminRoleManagement: 1,
    }


class MixedWorkloadUser(HttpUser):
    """
    Realistic mixed workload
    - Kombinasi kasir + admin operations
    - Various transaction sizes
    - Real-world patterns
    
    Weight: 10%
    """
    host = BASE_URL
    wait_time = between(1, 4)
    weight = 10
    
    tasks = {
        RealisticPOSWorkload: 1,
    }


class RushHourUser(HttpUser):
    """
    Simulasi jam sibuk
    - Minimal think time
    - Quick transactions
    - High transaction rate
    """
    host = BASE_URL
    wait_time = between(0.1, 0.5)
    weight = 15
    
    tasks = {
        RushHourSimulation: 1,
    }


class EnduranceTestUser(HttpUser):
    """
    Long-running endurance test
    - Normal wait time
    - Consistent load
    - Memory leak detection
    """
    host = BASE_URL
    wait_time = between(2, 5)
    weight = 30
    
    tasks = {
        EnduranceTestingFlow: 1,
    }


class AuthenticationTestUser(HttpUser):
    """
    Focus on authentication flows
    - Signup
    - Login/logout cycles
    - Different roles
    - Concurrent logins
    """
    host = BASE_URL
    wait_time = between(1, 3)
    weight = 10
    
    tasks = {
        SignupLoginFlow: 3,
        LoginWithDifferentRoles: 5,
        ConcurrentLoginStressTest: 2,
    }


class EdgeCaseUser(HttpUser):
    """
    Test edge cases dan error handling
    - Stock depletion
    - Promo abuse
    - Invalid operations
    """
    host = BASE_URL
    wait_time = between(0.5, 2)
    weight = 5
    
    tasks = {
        StockDepletionScenario: 5,
        PromoCodeAbuseTesting: 3,
        CheckoutWithVariousScenarios: 2,
    }


from locust import events
import logging

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logging.info("=" * 60)
    logging.info("🚀 SMART POS PERFORMANCE TEST STARTED")
    logging.info("=" * 60)
    logging.info(f"Target URL: {BASE_URL}")
    logging.info(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    logging.info("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logging.info("=" * 60)
    logging.info("🛑 SMART POS PERFORMANCE TEST STOPPED")
    logging.info("=" * 60)
    
    # Print summary
    stats = environment.stats.total
    logging.info(f"Total Requests: {stats.num_requests}")
    logging.info(f"Total Failures: {stats.num_failures}")
    logging.info(f"Failure Rate: {stats.fail_ratio * 100:.2f}%")
    logging.info(f"Average Response Time: {stats.avg_response_time:.2f}ms")
    logging.info(f"RPS: {stats.total_rps:.2f}")
    logging.info("=" * 60)


# from locust import LoadTestShape

# class StepLoadShape(LoadTestShape):
#     stages = [
#         {"duration": 120, "users": 10, "spawn_rate": 2},
#         {"duration": 240, "users": 25, "spawn_rate": 3},
#         {"duration": 420, "users": 50, "spawn_rate": 5},
#         {"duration": 600, "users": 100, "spawn_rate": 10},
#     ]
    
#     def tick(self):
#         run_time = self.get_run_time()
        
#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 return (stage["users"], stage["spawn_rate"])
        
#         return None  # Stop test


# To use custom shape, run:
# locust -f locustfile.py --shape StepLoadShape --headless