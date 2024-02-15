Feature: Invite

  Scenario: Administrator generates verification code with role "student"
    When the Administrator clicks the "invite" button
    And chooses role "student"
    Then verification code with role "student" is generated

  Scenario: Administrator generates verification code with role "council_member"
    When the Administrator clicks the "invite" button
    And chooses role "council_member"
    Then verification code with role "council_member" is generated

  Scenario: Administrator generates verification code with role "admin"
    When the Administrator clicks the "invite" button
    And chooses role "admin"
    Then verification code with role "admin" is generated

  Scenario: Client registers using verification code with "student" role
    Given there is verification code "1234" with role "student"
    When the Client types in verification code "1234" in register dialogue
    And the Client types in name "John Doe" in register dialogue
    And the Client types in academic group "5130904/00104" in register dialogue
    And the Client clicks "done" button
    Then the Client is registered with role "student"

  Scenario: Client registers using verification code with "council_member" role
    Given there is verification code "1234" with role "council_member"
    When the Client types in verification code "1234" in register dialogue
    And the Client types in name "John Doe" in register dialogue
    And the Client types in academic group "5130904/00104" in register dialogue
    Then the Client is registered with role "council_member"

  Scenario: Client registers using verification code with "council_member" role
    Given there is verification code "1234" with role "council_member"
    When the Client types in verification code "1234" in register dialogue
    And the Client types in name "John Doe" in register dialogue
    And the Client types in academic group "5130904/00104" in register dialogue
    Then the Client is registered with role "council_member"

  Scenario: Client registers using invalid verification code
    Given there is no verification code "1234"
    When the Client types in verification code "1234" in register dialogue
    Then error message "Invalid verification code" is sent

  Scenario: Client registers using invalid name
    When the Client types in name "kek[[[" in register dialogue
    Then error message "Invalid name" is sent

  Scenario: Client registers using invalid group
    When the Client types in group "1312" in register dialogue
    Then error message "Invalid group" is sent
