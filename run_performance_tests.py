#!/usr/bin/env python3
"""
Smart POS Performance Test Runner
Automated script untuk menjalankan berbagai profile testing
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
from load_test_config import LOAD_TEST_PROFILES

def run_test(profile_name, output_dir="performance_tests/results"):
    """
    Run performance test dengan profile tertentu
    """
    if profile_name not in LOAD_TEST_PROFILES:
        print(f"❌ Error: Profile '{profile_name}' tidak ditemukan!")
        print(f"Available profiles: {', '.join(LOAD_TEST_PROFILES.keys())}")
        return False
    
    profile = LOAD_TEST_PROFILES[profile_name]
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate report filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = f"{output_dir}/{profile_name}_{timestamp}.html"
    csv_report = f"{output_dir}/{profile_name}_{timestamp}_stats.csv"
    
    print("=" * 70)
    print(f"🚀 Running: {profile_name.upper()}")
    print("=" * 70)
    print(f"Description: {profile['description']}")
    print(f"Users: {profile['users']}")
    print(f"Spawn Rate: {profile['spawn_rate']}/sec")
    print(f"Duration: {profile['duration']}")
    print(f"HTML Report: {html_report}")
    print(f"CSV Report: {csv_report}")
    print("=" * 70)
    
    # Build locust command
    cmd = [
        "locust",
        "--headless",
        "-u", str(profile['users']),
        "-r", str(profile['spawn_rate']),
        "-t", profile['duration'],
        "--html", html_report,
        "--csv", csv_report.replace("_stats.csv", ""),
        "--loglevel", "INFO"
    ]
    
    try:
        # Run locust
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 70)
        print(f"✅ Test completed successfully!")
        print(f"📊 View report: {html_report}")
        print("=" * 70 + "\n")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print(f"❌ Test failed with error code {e.returncode}")
        print("=" * 70 + "\n")
        return False
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("⚠️  Test interrupted by user")
        print("=" * 70 + "\n")
        return False


def run_all_tests():
    """
    Run all test profiles sequentially
    """
    print("\n" + "=" * 70)
    print("🎯 RUNNING ALL TEST PROFILES")
    print("=" * 70 + "\n")
    
    results = {}
    
    for profile_name in LOAD_TEST_PROFILES.keys():
        success = run_test(profile_name)
        results[profile_name] = "✅ PASSED" if success else "❌ FAILED"
        
        # Wait between tests
        if profile_name != list(LOAD_TEST_PROFILES.keys())[-1]:
            print("\n⏳ Waiting 30 seconds before next test...\n")
            import time
            time.sleep(30)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    for profile, status in results.items():
        print(f"{status} - {profile}")
    print("=" * 70 + "\n")


def list_profiles():
    """
    List available test profiles
    """
    print("\n" + "=" * 70)
    print("📋 AVAILABLE TEST PROFILES")
    print("=" * 70 + "\n")
    
    for name, profile in LOAD_TEST_PROFILES.items():
        print(f"🔹 {name}")
        print(f"   Description: {profile['description']}")
        print(f"   Users: {profile['users']}")
        print(f"   Spawn Rate: {profile['spawn_rate']}/sec")
        print(f"   Duration: {profile['duration']}")
        print()
    
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Smart POS Performance Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_performance_tests.py --list
  python run_performance_tests.py --profile normal_load
  python run_performance_tests.py --all
  python run_performance_tests.py --profile stress_test --output custom_results/
        """
    )
    
    parser.add_argument(
        "--profile",
        choices=LOAD_TEST_PROFILES.keys(),
        help="Specific test profile to run"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all test profiles sequentially"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available test profiles"
    )
    
    parser.add_argument(
        "--output",
        default="performance_tests/results",
        help="Output directory for reports (default: performance_tests/results)"
    )
    
    args = parser.parse_args()
    
    # Check if Flask app is running
    import requests
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=2)
        print("✅ Flask app is running\n")
    except requests.exceptions.RequestException:
        print("❌ Error: Flask app is not running!")
        print("Please start the Flask app first: python app.py\n")
        sys.exit(1)
    
    # Execute based on arguments
    if args.list:
        list_profiles()
    elif args.all:
        run_all_tests()
    elif args.profile:
        run_test(args.profile, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()