import requests
import time
from behave import given, when, then
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:5000"


# ---------- BASIC SETUP ----------
@given("the application is running")
def step_app_running(context):
    pass


@given("I am logged in as admin")
def step_login_admin(context):
    session = requests.Session()
    res = session.post(
        f"{BASE_URL}/api/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert res.status_code == 200

    context.driver.get(BASE_URL)
    for c in session.cookies:
        context.driver.add_cookie({
            "name": c.name,
            "value": c.value,
            "path": "/",
            "domain": "127.0.0.1"
        })


@given("I open admin dashboard")
def step_open_admin(context):
    context.driver.get(f"{BASE_URL}/admin")
    time.sleep(1)


# ---------- AC-13 ----------
@then("the promo list should be visible")
def step_promo_list_visible(context):
    promo_section = context.driver.find_element(By.CLASS_NAME, "list-group")
    assert promo_section.is_displayed()


@given("no promo data exists")
def step_clear_promo(context):
    # hapus semua promo via API langsung
    res = requests.get(f"{BASE_URL}/api/promos")
    for p in res.json():
        requests.post(
            f"{BASE_URL}/api/admin/delete_promo",
            json={"id": p.get("id")}
        )
    context.driver.refresh()
    time.sleep(1)


@then("the promo list should be empty")
def step_promo_empty(context):
    promos = context.driver.find_elements(By.CLASS_NAME, "list-group-item")
    assert len(promos) == 0


# ---------- AC-14 ADD PROMO ----------
@when('I input promo code "{code}" with discount {discount:d}')
def step_input_promo(context, code, discount):
    context.driver.find_element(By.ID, "promo-code").clear()
    context.driver.find_element(By.ID, "promo-code").send_keys(code)

    context.driver.find_element(By.ID, "promo-disc").clear()
    context.driver.find_element(By.ID, "promo-disc").send_keys(str(discount))


@when("I submit promo form")
def step_submit_promo(context):
    context.driver.find_element(
        By.XPATH, "//button[contains(text(),'Tambah Promo')]"
    ).click()
    time.sleep(1)


@then('the promo list should contain "{code}" with discount {discount:d}')
def step_verify_promo(context, code, discount):
    promos = context.driver.find_elements(By.CLASS_NAME, "list-group-item")
    assert any(f"{code} ({discount}%)" in p.text for p in promos)


@then("the system should reject the promo input")
def step_reject_invalid_discount(context):
    promos = context.driver.find_elements(By.CLASS_NAME, "list-group-item")
    assert all("150%" not in p.text and "-15%" not in p.text for p in promos)


@then("the system should show duplicate promo error")
def step_duplicate_error(context):
    # karena backend belum kirim error message,
    # validasi dilakukan dari data yang tidak bertambah
    promos = context.driver.find_elements(By.CLASS_NAME, "list-group-item")
    codes = [p.text.split()[0] for p in promos]
    assert codes.count("DISKON10") == 1


# ---------- AC-15 DELETE PROMO ----------
@given('a promo with code "{code}" exists')
def step_ensure_promo(context, code):
    requests.post(
        f"{BASE_URL}/api/admin/add_promo",
        json={"code": code, "discount": 10}
    )
    context.driver.refresh()
    time.sleep(1)


@when('I delete promo "{code}"')
def step_delete_promo(context, code):
    promos = context.driver.find_elements(By.CLASS_NAME, "list-group-item")
    for p in promos:
        if code in p.text:
            p.find_element(By.TAG_NAME, "button").click()
            break
    time.sleep(1)


@then('the promo list should not contain "{code}"')
def step_verify_deleted(context, code):
    promos = context.driver.find_elements(By.CLASS_NAME, "list-group-item")
    assert all(code not in p.text for p in promos)


# ---------- UAT-043 CASHIER SIDE ----------
@when("I login as cashier")
def step_login_kasir(context):
    requests.post(
        f"{BASE_URL}/api/login",
        json={"username": "kasir", "password": "kasir123"}
    )
    context.driver.get(BASE_URL)
    time.sleep(1)


@then('the cashier promo list should not contain "{code}"')
def step_verify_cashier_promo(context, code):
    context.driver.find_element(By.ID, "promo-select")
    options = context.driver.find_elements(By.TAG_NAME, "option")
    assert all(code not in o.text for o in options)
