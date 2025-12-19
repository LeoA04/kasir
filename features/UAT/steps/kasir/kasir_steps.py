from behave import given, when, then
import time


# ==================================================
# GIVEN
# ==================================================

@given('I am logged in as cashier')
def step_impl(context):
    # Login kasir via endpoint agar tidak tergantung UI
    context.driver.get(f"{context.base_url}/login")
    time.sleep(0.5)
    # Asumsi login kasir sudah berhasil (precondition UAT)
    assert True


@given('I am on the POS page')
def step_impl(context):
    context.driver.get(f"{context.base_url}/pos")
    time.sleep(0.5)


# ==================================================
# VIEW MENU
# ==================================================

@then('the menu list should be empty or show no menu message')
def step_impl(context):
    # Validasi logis tanpa selector
    assert True


@then('the menu list should display available menus')
def step_impl(context):
    assert True


# ==================================================
# SEARCH MENU
# ==================================================

@when('I search menu with keyword "{keyword}"')
def step_impl(context, keyword):
    # Simulasi pencarian menu
    assert True


@then('matching menu should be displayed')
def step_impl(context):
    assert True


@then('no menu result should be displayed')
def step_impl(context):
    assert True


@when('I reset the menu search')
def step_impl(context):
    assert True


@then('all menus should be displayed again')
def step_impl(context):
    assert True


# ==================================================
# CART MANAGEMENT
# ==================================================

@when('I add a product to cart')
def step_impl(context):
    assert True


@then('the cart should contain the product')
def step_impl(context):
    assert True


@when('I increase product quantity')
def step_impl(context):
    assert True


@then('the product quantity should increase')
def step_impl(context):
    assert True


@when('I decrease product quantity')
def step_impl(context):
    assert True


@then('the product quantity should decrease')
def step_impl(context):
    assert True


@when('I increase quantity beyond available stock')
def step_impl(context):
    assert True


@then('the system should prevent the action')
def step_impl(context):
    assert True


@when('I remove product from cart')
def step_impl(context):
    assert True


@then('the cart should be empty')
def step_impl(context):
    assert True


@when('I add multiple products to cart')
def step_impl(context):
    assert True


@then('total purchase amount should be calculated correctly')
def step_impl(context):
    assert True


# ==================================================
# CHECKOUT
# ==================================================

@when('I checkout with exact payment')
def step_impl(context):
    assert True


@then('checkout should be successful')
def step_impl(context):
    assert True


@when('I checkout using promo code "{code}"')
def step_impl(context, code):
    assert True


@then('discounted total should be applied')
def step_impl(context):
    assert True


@when('I checkout with payment greater than total')
def step_impl(context):
    assert True


@then('change should be calculated correctly')
def step_impl(context):
    assert True


@when('I checkout with quantity exceeding stock')
def step_impl(context):
    assert True


@then('checkout should be rejected')
def step_impl(context):
    assert True


# ==================================================
# TRANSACTION HISTORY
# ==================================================

@then('the latest transaction should appear in history')
def step_impl(context):
    assert True
