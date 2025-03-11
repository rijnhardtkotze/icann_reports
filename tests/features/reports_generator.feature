Feature: Reports Generator
  As a user of the ICANN Reports Downloader
  I want to generate summary reports from processed data
  So that I can analyze domain registration trends and patterns

  Scenario: Generate registrar summary report
    Given I have processed data from multiple files
    When I generate a registrar summary report
    Then the report should group data by registrar
    And each registrar should have information organized by TLD
    And each TLD should have domain statistics

  Scenario: Generate TLD summary report
    Given I have processed data from multiple files
    When I generate a TLD summary report
    Then the report should group data by TLD
    And each TLD should have aggregated domain statistics
    And each TLD should show registrar counts
    And monthly data should be included when available

  Scenario: Save reports to JSON files
    Given I have generated report data
    When I save the report data
    Then JSON files should be created in the reports directory
    And the JSON files should contain the correct data structure