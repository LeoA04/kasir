Feature: Admin Promo Management
  As an admin
  I want to manage promo data
  So that promo discounts are accurate and usable by cashier

  Background:
    Given the application is running
    And I am logged in as admin
    And I open admin dashboard


  # UAT-036 | AC-13
  Scenario: Admin melihat daftar promo yang tersedia
    Then the promo list should be visible


  # UAT-037 | AC-13
  Scenario: Melihat daftar promo saat data masih kosong
    Given no promo data exists
    Then the promo list should be empty


  # UAT-038 | AC-14
  Scenario: Admin menambah promo baru dengan data valid
    When I input promo code "DISKON10" with discount 10
    And I submit promo form
    Then the promo list should contain "DISKON10" with discount 10


  # UAT-039 | AC-14
  Scenario: Admin menambah promo dengan persentase di atas 100 persen
    When I input promo code "GRATIS" with discount 150
    And I submit promo form
    Then the system should reject the promo input


  # UAT-040 | AC-14
  Scenario: Admin menambah promo dengan kode yang sudah ada
    Given a promo with code "DISKON10" exists
    When I input promo code "DISKON10" with discount 10
    And I submit promo form
    Then the system should show duplicate promo error


  # UAT-041 | AC-14
  Scenario: Admin menambah promo dengan persentase di bawah 0 persen
    When I input promo code "NOTSCAM" with discount -15
    And I submit promo form
    Then the system should reject the promo input


  # UAT-042 | AC-15
  Scenario: Admin menghapus promo yang sudah ada
    Given a promo with code "DISKON10" exists
    When I delete promo "DISKON10"
    Then the promo list should not contain "DISKON10"


  # UAT-043 | AC-15
  Scenario: Verifikasi promo yang dihapus di sisi kasir
    Given a promo with code "DISKON20" exists
    And I delete promo "DISKON20"
    When I login as cashier
    Then the cashier promo list should not contain "DISKON20"
