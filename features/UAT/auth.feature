
Feature: Authentication (Signup & Login)
  As a user
  I want to signup and login
  So that I can access the Smart POS system

  # =====================
  # ACCEPTANCE CRITERIA 1 - SIGNUP
  # =====================

  Scenario: UAT-001 User signup successfully (new username)
    Given I am on the signup page
    When I signup with username "owen" password "owen123" confirm "owen123"
    Then signup should be successful

  Scenario: UAT-002 User signup failed (username already exists)
    Given I am on the signup page
    When I signup with username "owen" password "owen123" confirm "owen123"
    Then I should see signup error message "Username sudah ada"

  Scenario: UAT-003 User signup failed (password confirmation mismatch)
    Given I am on the signup page
    When I signup with username "adam" password "adam123" confirm "adam1234"
    Then I should see signup error message "Password dan konfirmasi password tidak sama!"

  Scenario: UAT-004 User signup failed (password less than 6 characters)
    Given I am on the signup page
    When I signup with username "adam" password "adam1" confirm "adam1"
    Then I should see signup error message "Password minimal 6 karakter"


  # =====================
  # ACCEPTANCE CRITERIA 2 - LOGIN
  # =====================

  Scenario: UAT-005 User login success (role approved)
    Given I am on the login page
    When I login with username "rafael" and password "rafael123"
    Then login should be successful

  Scenario: UAT-006 User login failed (role not approved)
    Given I am on the login page
    When I login with username "owen" and password "owen123"
    Then I should see role not approved message

  Scenario: UAT-007 User login failed (username not registered)
    Given I am on the login page
    When I login with username "justin" and password "justin123"
    Then I should see login error message

  Scenario: UAT-008 User login failed (wrong password)
    Given I am on the login page
    When I login with username "owen" and password "owen1234"
    Then I should see login error message
