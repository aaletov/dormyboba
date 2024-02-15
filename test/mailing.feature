Feature: Mailing

  Scenario: Administrator creates mailing without text
    Given the Administrator have not filled mailing text
    When the Administrator clicks "done" button
    Then error message "Mailing text is not filled" sent

  Scenario: Administrator creates simple mailing
    When the Administrator clicks "Set text" button
    And types in "sonic the hedgehog"
    And clicks "done" button
    Then message "sonic the hedgehog" is sent to all users

  Scenario: Administrator creates mailing with theme
    When the Administrator clicks "Set text" button
    And types in "sonic the hedgehog"
    And clicks "Set theme" button
    And types in "i love sonic the hedgehog"
    And clicks "done" button
    Then message is sent to all users
    And message header is "i love sonic the hedgehog"
    And there is blank line after header
    And message text is "sonic the hedgehog"

  Scenario: Administrator creates mailing only for ICST students
    Given the Administrator have set text
    When the Administrator clicks "Set filters" button
    And the Administrator clicks "Set institute" button
    And the Administrator clicks "ICST" button
    And the Administrator clicks "done" button
    Then message is sent to all users from ICST institute

  Scenario: Administrator creates mailing only for first year students
    Given the Administrator have set text
    When the Administrator clicks "Set filters" button
    And the Administrator clicks "Set course" button
    And the Administrator clicks "1" button
    And the Administrator clicks "done" button
    Then message is sent to all first year users

  Scenario: Administrator creates mailing only for masters students
    Given the Administrator have set text
    When the Administrator clicks "Set filters" button
    And the Administrator clicks "Set academic type" button
    And the Administrator clicks "Master" button
    And the Administrator clicks "done" button
    Then message is sent to all masters users

  Scenario: Administrator creates delayed mailing
    Given the Administrator have set text
    When the Administrator clicks "Set time"
    And the Administrator types in "14:00:00"
    Then message is sent to all users at 14:00:00 (ignore timezone)

  Scenario: Administrator sents incorrect time
    When the Administrator clicks "Set time" button
    And the Administrator types in "590390"
    Then error message "Time should be in format 23:59:59" is sent
