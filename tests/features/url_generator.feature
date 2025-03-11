Feature: URL Generator
  As a user of the ICANN Reports Downloader
  I want to generate URLs for downloading reports
  So that I can access the required reports for specific TLDs and time periods

  Scenario: Generate URLs for a single TLD with a date range
    Given I have a TLD configuration for "com" from "2024-01" to "2024-03"
    When I generate the URLs
    Then I should get 3 URLs for the "com" TLD
    And each URL should follow the correct format for ICANN reports
    And the URLs should include the months "202401", "202402", and "202403"

  Scenario: Generate URLs for multiple TLDs
    Given I have a TLD configuration for "com" from "2024-01" to "2024-02"
    And I have a TLD configuration for "net" from "2024-01" to "2024-02"
    When I generate the URLs
    Then I should get 4 URLs for the specified TLDs
    And 2 URLs should be for the "com" TLD
    And 2 URLs should be for the "net" TLD

  Scenario: Parse date from filename
    Given I have a filename "com-transactions-202401-en.csv"
    When I parse the date from the filename
    Then I should get the date "2024-01"