#!/usr/bin/env python3
"""
Setup Test Data for Performance Testing
Script untuk prepare database dengan test data
"""

from app import app, db, User, Product, Promo, Transaction
from werkzeug.security import generate_password_hash
from load_test_config import TEST_USERS, TEST_PRODUCTS, TEST_PROMOS

def clear_database():
    print("🗑️  Clearing database...")
    
    with app.app_context():
        db.session.query(Transaction).delete()
        db.session.query(Promo).delete()
        db.session.query(Product).delete()
        
        db.session.query(User).filter(User.username != 'admin').delete()
        db.session.commit()
    
    print("✅ Database cleared!")


def create_test_users():
    print("\n👥 Creating test users...")
    
    with app.app_context():
        for username, credentials in TEST_USERS.items():
            existing = User.query.filter_by(username=username).first()
            
            if not existing:
                user = User(
                    username=credentials["username"],
                    password=generate_password_hash(credentials["password"]),
                    role=credentials["role"]
                )
                db.session.add(user)
                print(f"   ✓ Created {username} ({credentials['role']})")
            else:
                print(f"   ⊘ {username} already exists")
        
        db.session.commit()
    
    print("✅ Test users created!")


def create_test_products():
    print("\n📦 Creating test products...")
    
    with app.app_context():
        for product_data in TEST_PRODUCTS:
            existing = Product.query.filter_by(name=product_data["name"]).first()
            
            if not existing:
                product = Product(**product_data)
                db.session.add(product)
                print(f"   ✓ Created {product_data['name']} (Rp {product_data['price']})")
            else:
                # Update stock if exists
                existing.stock = product_data["stock"]
                print(f"   ⟳ Updated {product_data['name']} stock to {product_data['stock']}")
        
        db.session.commit()
    
    print("✅ Test products created!")


def create_test_promos():
    print("\n🎫 Creating test promos...")
    
    with app.app_context():
        for promo_data in TEST_PROMOS:
            existing = Promo.query.filter_by(code=promo_data["code"]).first()
            
            if not existing:
                promo = Promo(**promo_data)
                db.session.add(promo)
                print(f"   ✓ Created {promo_data['code']} ({promo_data['discount_percent']}%)")
            else:
                print(f"   ⊘ {promo_data['code']} already exists")
        
        db.session.commit()
    
    print("✅ Test promos created!")


def verify_setup():
    print("\n🔍 Verifying setup...")
    
    with app.app_context():
        user_count = User.query.count()
        product_count = Product.query.count()
        promo_count = Promo.query.count()
        
        print(f"   Users: {user_count}")
        print(f"   Products: {product_count}")
        print(f"   Promos: {promo_count}")
        
        if user_count >= 4 and product_count >= 5 and promo_count >= 3:
            print("✅ Setup verified successfully!")
            return True
        else:
            print("❌ Setup incomplete!")
            return False


def display_summary():
    print("\n" + "=" * 70)
    print("📊 TEST DATA SUMMARY")
    print("=" * 70)
    
    with app.app_context():
        print("\n👥 Test Users:")
        for user in User.query.all():
            print(f"   • {user.username} ({user.role})")
        
        print("\n📦 Test Products:")
        for product in Product.query.all():
            print(f"   • {product.name} - Rp {product.price:,} (Stock: {product.stock})")
        
        print("\n🎫 Test Promos:")
        for promo in Promo.query.all():
            print(f"   • {promo.code} - {promo.discount_percent}% discount")
    
    print("\n" + "=" * 70)


def reset_stock():
    print("\n🔄 Resetting product stocks...")
    
    with app.app_context():
        for product in Product.query.all():
            product.stock = 100
            print(f"   ✓ Reset {product.name} stock to 100")
        
        db.session.commit()
    
    print("✅ Stocks reset!")


def main():
    import sys
    
    print("\n" + "=" * 70)
    print("🚀 SMART POS - PERFORMANCE TESTING SETUP")
    print("=" * 70)
    
    # Check if Flask app database exists
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"\n❌ Error: Could not connect to database!")
        print(f"   {str(e)}")
        sys.exit(1)
    
    while True:
        print("\n" + "=" * 70)
        print("📋 SETUP OPTIONS")
        print("=" * 70)
        print("1. Full Setup (Clear & Create All)")
        print("2. Create Test Users Only")
        print("3. Create Test Products Only")
        print("4. Create Test Promos Only")
        print("5. Reset Product Stocks")
        print("6. View Current Data")
        print("7. Clear Database")
        print("0. Exit")
        print("=" * 70)
        
        choice = input("\nSelect option (0-7): ").strip()
        
        if choice == "1":
            print("\n⚠️  WARNING: This will clear all test data!")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                clear_database()
                create_test_users()
                create_test_products()
                create_test_promos()
                verify_setup()
                display_summary()
                print("\n✅ Full setup completed!")
            else:
                print("❌ Setup cancelled")
        
        elif choice == "2":
            create_test_users()
        
        elif choice == "3":
            create_test_products()
        
        elif choice == "4":
            create_test_promos()
        
        elif choice == "5":
            reset_stock()
        
        elif choice == "6":
            display_summary()
        
        elif choice == "7":
            print("\n⚠️  WARNING: This will delete all test data!")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                clear_database()
            else:
                print("❌ Clear cancelled")
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid option!")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()