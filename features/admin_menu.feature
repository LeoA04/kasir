Feature: Admin Menu Management
  As an admin
  I want to manage menu data
  So that products in the POS system are accurate and up to date


  # ==================================================
  # ACCEPTANCE CRITERIA 8 – MELIHAT MENU
  # ==================================================

  Scenario: UAT-025 Admin melihat daftar menu yang tersedia
    Given I am logged in as admin
    When I open admin menu page
    Then I should see menu table


  # ==================================================
  # ACCEPTANCE CRITERIA 9 – MENAMBAH MENU
  # ==================================================

  Scenario: UAT-026 Admin menambah menu baru dengan data lengkap
    Given I am logged in as admin
    When I add new menu with name "Es Teh", price "5000", stock "50", category "Minuman"
    Then the menu "Es Teh" should appear in menu list

  Scenario: UAT-027 Admin menambah menu dengan stok kosong
    Given I am logged in as admin
    When I add new menu with name "Ayam Goreng", price "12000", stock "", category "Makanan"
    Then I should see menu validation error

  Scenario: UAT-028 Admin menambah menu dengan harga kosong
    Given I am logged in as admin
    When I add new menu with name "Ayam Goreng", price "", stock "25", category "Makanan"
    Then I should see menu validation error

  Scenario: UAT-029 Admin menambah menu dengan harga atau stok bernilai negatif
    Given I am logged in as admin
    When I add new menu with name "Ayam Geprek", price "-16000", stock "-25", category "Makanan"
    Then I should see menu validation error


  # ==================================================
  # ACCEPTANCE CRITERIA 10 – MENGHAPUS MENU
  # ==================================================

  Scenario: UAT-030 Admin menghapus salah satu menu yang ada
    Given I am logged in as admin
    And menu "Es Teh" exists
    When I delete menu "Es Teh"
    Then the menu "Es Teh" should not exist in menu list

  Scenario: UAT-031 Admin gagal menghapus menu yang sedang dalam transaksi aktif
    Given I am logged in as admin
    And menu is currently used in active transaction
    When I attempt to delete the menu
    Then menu deletion should be blocked


  # ==================================================
  # ACCEPTANCE CRITERIA 11 – UPDATE STOK
  # ==================================================

  Scenario: UAT-032 Admin melakukan update stok (restock) dengan nilai positif
    Given I am logged in as admin
    And menu stock is low
    When I update menu stock with positive value
    Then menu stock should be increased

  Scenario: UAT-033 Admin gagal update stok dengan nilai negatif
    Given I am logged in as admin
    And menu stock is low
    When I update menu stock with negative value
    Then I should see stock validation error


  # ==================================================
  # ACCEPTANCE CRITERIA 12 – PENCARIAN MENU
  # ==================================================

  Scenario: UAT-034 Admin mencari menu berdasarkan nama yang ada
    Given I am logged in as admin
    And menu "Es Teh" exists
    When I search menu with keyword "Es Teh"
    Then I should see menu "Es Teh" in search result

  Scenario: UAT-035 Admin mencari menu yang tidak terdaftar
    Given I am logged in as admin
    When I search menu with keyword "Baguette"
    Then I should see no menu result

  Scenario: UAT-036 Admin reset pencarian menu
    Given I am logged in as admin
    And menu "Es Teh" exists
    When I search menu with keyword "Es Teh"
    And I reset menu search
    Then I should see all menu items
