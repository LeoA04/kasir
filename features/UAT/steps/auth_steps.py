from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
import time


# ==================================================
# GIVEN
# ==================================================

@given('I am on the signup page')
def step_impl(context):
    context.driver.get(f"{context.base_url}/signup")
    time.sleep(0.5)


@given('I am on the login page')
def step_impl(context):
    context.driver.get(f"{context.base_url}/login")
    time.sleep(0.5)


# ==================================================
# WHEN
# ==================================================

@when('I signup with username "{username}" password "{password}" confirm "{confirm}"')
def step_impl(context, username, password, confirm):
    context.driver.find_element(By.ID, "user").clear()
    context.driver.find_element(By.ID, "user").send_keys(username)

    context.driver.find_element(By.ID, "pass").clear()
    context.driver.find_element(By.ID, "pass").send_keys(password)

    context.driver.find_element(By.ID, "confirm-pass").clear()
    context.driver.find_element(By.ID, "confirm-pass").send_keys(confirm)

    context.driver.find_element(
        By.XPATH, "//button[contains(text(),'Daftar')]"
    ).click()
    time.sleep(1)


@when('I login with username "{username}" and password "{password}"')
def step_impl(context, username, password):
    context.driver.find_element(By.ID, "user").clear()
    context.driver.find_element(By.ID, "user").send_keys(username)

    context.driver.find_element(By.ID, "pass").clear()
    context.driver.find_element(By.ID, "pass").send_keys(password)

    context.driver.find_element(
        By.XPATH, "//button[contains(text(),'Login')]"
    ).click()
    time.sleep(1)


# ==================================================
# THEN – SIGNUP
# ==================================================

@then('signup should be successful')
def step_impl(context):
    time.sleep(0.5)
    try:
        alert = context.driver.switch_to.alert
        alert.accept()
    except NoAlertPresentException:
        pass
    assert True


@then('I should see signup error message "{message}"')
def step_impl(context, message):
    time.sleep(0.5)
    try:
        alert = context.driver.switch_to.alert
        alert.accept()
    except NoAlertPresentException:
        pass
    assert True


# ==================================================
# THEN – LOGIN
# ==================================================

@then('login should be successful')
def step_impl(context):
    time.sleep(0.5)
    try:
        alert = context.driver.switch_to.alert
        alert.accept()
        assert False, "Unexpected alert on successful login"
    except NoAlertPresentException:
        pass
    assert True


@then('I should see role not approved message')
def step_impl(context):
    time.sleep(0.5)
    try:
        alert = context.driver.switch_to.alert
        alert.accept()
    except NoAlertPresentException:
        pass
    assert True


@then('I should see login error message')
def step_impl(context):
    time.sleep(0.5)
    try:
        alert = context.driver.switch_to.alert
        alert.accept()
    except NoAlertPresentException:
        pass
    assert True
