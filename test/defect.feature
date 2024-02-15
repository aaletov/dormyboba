Feature: Defect

  Scenario: Client creates defect with "electricity" type
    When the Client chooses defect type "electricity"
    And types in defect description "socket broken"
    And clicks "done" button
    Then defect is created in google sheets
    And type is "electricity"
    And description is "socket broken"
    And status is "created"
    And message with info about defect is sent to random Administrator
    And message contains "accept" button

  Scenario: Client creates defect with "plumb" type
    When the Client chooses defect type "plumb"
    And types in defect description "my drain not draining"
    And clicks "done" button
    Then defect is created in google sheets
    And type is "plumb"
    And description is "my drain not draining"
    And status is "created"
    And message with info about defect is sent to random Administrator
    And message contains "accept" button

  Scenario: Client creates defect with "common" type
    When the Client chooses defect type "common"
    And types in defect description "i have no food"
    And clicks "done" button
    Then defect is created in google sheets
    And type is "common"
    And description is "i have no food"
    And status is "created"
    And message with info about defect is sent to random Administrator
    And message contains "accept" button

  Scenario: Client clicks "done" button before choosing type
    Given the Client have not chosen defect type
    When the Client clicks "done" button
    Then error message "Defect type is not chosen" is sent

  Scenario: Client clicks "done" button before filling description
    Given the Client have chosen defect type
    And the Client didn't filled description
    When the Client clicks "done" button
    Then error message "Description is not filled" is sent
