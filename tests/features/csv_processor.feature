Feature: CSV Processor
  As a user of the ICANN Reports Downloader
  I want to process CSV files containing ICANN registrar data
  So that I can normalize field names and extract meaningful data

  Scenario: Process a CSV file with standard headers
    Given I have a CSV file with standard headers
    When I process the CSV file
    Then the field names should be normalized
    And the rows should be parsed correctly

  Scenario: Process a CSV file with non-standard headers
    Given I have a CSV file with non-standard headers
    When I process the CSV file
    Then the field names should be mapped to standard names
    And the rows should be parsed with normalized field names

  Scenario: Process a CSV file missing the TLD field
    Given I have a CSV file with name "com-transactions-202401-en.csv" missing the TLD field
    When I process the CSV file
    Then the TLD field should be inferred from the filename
    And the value "COM" should be set for the TLD field in all rows

  Scenario: Skip already processed files
    Given I have a CSV file that has already been processed
    When I process the CSV file
    Then the file should be skipped
    And no data should be returned