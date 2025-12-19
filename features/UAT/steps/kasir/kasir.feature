Feature: Cashier POS Transaction
  As a cashier
  I want to manage sales transactions
  So that I can process customer orders correctly

  Background:
    Given I am logged in as cashier
    And I am on the POS page

  # =====================
  # AC-3 VIEW MENU
  # =====================

  Scenario: UAT-009 View menu when no menu is created by admin
    Then the menu list should be empty or show no menu message

  Scenario: UAT-009 View menu when menu is available
    Then the menu list should display available menus

  # =====================
  # AC-4 SEARCH MENU
  # =====================

  Scenario: UAT-010 Search menu with valid keyword
    When I search menu with keyword "Nasi"
    Then matching menu should be displayed

  Scenario: UAT-011 Search menu with invalid keyword
    When I search menu with keyword "Pizza"
    Then no menu result should be displayed

  Scenario: UAT-012 Reset menu search
    When I reset the menu search
    Then all menus should be displayed again

  # =====================
  # AC-5 CART MANAGEMENT
  # =====================

  Scenario: UAT-013 Add product to cart
    When I add a product to cart
    Then the cart should contain the product

  Scenario: UAT-014 Increase product quantity
    When I increase product quantity
    Then the product quantity should increase

  Scenario: UAT-015 Decrease product quantity
    When I decrease product quantity
    Then the product quantity should decrease

  Scenario: UAT-016 Increase quantity beyond stock
    When I increase quantity beyond available stock
    Then the system should prevent the action

  Scenario: UAT-017 Remove product from cart
    When I remove product from cart
    Then the cart should be empty

  Scenario: UAT-018 Calculate total purchase
    When I add multiple products to cart
    Then total purchase amount should be calculated correctly

  # =====================
  # AC-6 CHECKOUT
  # =====================

  Scenario: UAT-019 Checkout without promo
    When I checkout with exact payment
    Then checkout should be successful

  Scenario: UAT-020 Checkout with promo code
    When I checkout using promo code "BURGERONLY"
    Then discounted total should be applied

  Scenario: UAT-021 Checkout with change calculation
    When I checkout with payment greater than total
    Then change should be calculated correctly

  Scenario: UAT-022 Validate stock during checkout
    When I checkout with quantity exceeding stock
    Then checkout should be rejected

  # =====================
  # AC-7 TRANSACTION HISTORY
  # =====================

  Scenario: UAT-023 View recent transaction history
    Then the latest transaction should appear in history
