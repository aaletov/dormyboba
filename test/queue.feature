Feature: Queue

  Scenario: Administrator creates mailing without theme
    Given the Administrator have not filled queue theme
    When the Administrator clicks "done" button
    Then error message "Queue theme is not set" is sent

  Scenario: Administrator creates mailing without open time
    Given the Adminstrator have filled queue theme
    And the Administrator have not filled queue open time
    When the Administrator clicks "done" button
    Then error message "Open time is not set" is sent

  Scenario: Administrator creates simple queue
    When the Administrator clicks "Set theme" button
    And types in "peter the great"
    And the Administrator clicks "Set open time" button
    And types in "14:00:00"
    And the Administrator clicks "done" button
    Then message with "Queue is opened" header is sent to all users at 14:00:00
    And there is blank line after header
    And there is "peter the greate" line after blank line
    And message has "Join" button

  Scenario: Administrator creates queue with description
    When the Administrator clicks "Set theme" button
    And types in "peter the great"
    And the Administrator clicks "Set open time" button
    And types in "14:00:00"
    And the Administrator cliks "Set description" button
    And types in "i given uuup"
    And the Administrator clicks "done" button
    Then message with "Queue is opened" header is sent to all users at 14:00:00
    And there is blank line after header
    And there is "peter the greate" theme line after blank line
    And there is blank line after theme
    And there is "i given up" descritpion line after blank line
    And message has "Join" button

  Scenario: User joins empty queue
    Given queue is empty
    When the User clicks "Join" button
    Then message "Not it's your turn" is sent to the User
    And the message has "Done" button

  Scenario: User joins non-empty queue
    Given queue is not empty
    When the User clicks "Join" button
    Then the User is added to the end of the queue
    And message "You've joined queue" is sent to the User
    And the message has "Leave" button

  Scenario: User done in non-empty queue
    Given now it's user's turn
    When the User clicks "Done" button
    Then the User is deleted from queue
    And message "Not it's your turn" is sent to the next User
    And the message has "Done" button

  Scenario: User leaves queue
    Given the User is in the queue
    When the User clicks "Leave" button
    Then the User is deleted from queue
