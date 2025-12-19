BASE_URL = "http://127.0.0.1:5000"

# Response Time SLO (Service Level Objectives) dalam milliseconds
RESPONSE_TIME_SLO = {
    "fast": 500,      # Endpoint cepat (< 500ms)
    "normal": 1000,   # Endpoint normal (< 1s)
    "slow": 3000,     # Endpoint lambat tapi masih acceptable (< 3s)
}

TEST_USERS = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "kasir1": {"username": "kasir1", "password": "kasir123", "role": "kasir"},
    "kasir2": {"username": "kasir2", "password": "kasir123", "role": "kasir"},
    "user1": {"username": "user1", "password": "user123", "role": "user"},
}

TEST_PRODUCTS = [
    {"name": "Kopi Susu", "price": 15000, "stock": 100, "category": "minuman", "img": "☕"},
    {"name": "Teh Manis", "price": 10000, "stock": 100, "category": "minuman", "img": "🍵"},
    {"name": "Nasi Goreng", "price": 25000, "stock": 50, "category": "makanan", "img": "🍛"},
    {"name": "Mie Ayam", "price": 20000, "stock": 50, "category": "makanan", "img": "🍜"},
    {"name": "Roti Bakar", "price": 18000, "stock": 30, "category": "makanan", "img": "🍞"},
]

TEST_PROMOS = [
    {"code": "DISKON10", "discount_percent": 10},
    {"code": "HEMAT20", "discount_percent": 20},
    {"code": "PROMO50", "discount_percent": 50},
]

LOAD_TEST_PROFILES = {
    # Load Testing Normal - Simulasi beban harian normal
    "normal_load": {
        "users": 20,
        "spawn_rate": 2,
        "duration": "5m",
        "description": "Simulasi 20 users berbelanja normal"
    },
    
    # Stress Testing - Cari breaking point
    "stress_test": {
        "users": 100,
        "spawn_rate": 10,
        "duration": "10m",
        "description": "Stress test dengan 100 concurrent users"
    },
    
    # Spike Testing - Lonjakan mendadak
    "spike_test": {
        "users": 200,
        "spawn_rate": 50,  # Ramp up sangat cepat
        "duration": "3m",
        "description": "Spike test - lonjakan tiba-tiba 200 users"
    },
    
    # Endurance/Soak Testing - Durasi panjang
    "endurance_test": {
        "users": 30,
        "spawn_rate": 3,
        "duration": "30m",
        "description": "Endurance test selama 30 menit"
    },
    
    # Capacity Testing - Maksimal throughput
    "capacity_test": {
        "users": 500,
        "spawn_rate": 25,
        "duration": "15m",
        "description": "Capacity test - find maximum throughput"
    }
}

# Seberapa sering task dijalankan (higher = more frequent)
TASK_WEIGHTS = {
    "view_products": 10,      # Paling sering (browsing)
    "add_to_cart": 5,         # Sering
    "reduce_from_cart": 2,    # Jarang
    "checkout": 3,            # Medium
    "view_history": 2,        # Jarang
    "admin_operations": 1,    # Sangat jarang
}