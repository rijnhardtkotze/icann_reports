Feature: Field Validation
  As a user of the ICANN Reports Downloader
  I want to validate the data in CSV files
  So that I can ensure data quality and consistency

  Scenario: Validate a row with all required fields
    Given I have a row with all required fields
    When I validate the row
    Then the row should be valid
    And no validation errors should be reported

  Scenario: Validate a row with missing required fields
    Given I have a row missing some required fields
    When I validate the row
    Then the row should be invalid
    And validation errors should list the missing fields

  Scenario: Validate a row with incorrect field types
    Given I have a row with non-numeric values in numeric fields
    When I validate the row
    Then the row should be invalid
    And validation errors should report the type mismatches

  Scenario: Generate validation report
    Given I have validation results for multiple files
    When I generate a validation report
    Then the report should include a summary for each file
    And the report should list the number of valid and invalid rows
    And the report should include details of validation errors