Feature: User Authentication
  As a user, I want to be able to log in to my account securely
  so that I can access my profile and features.

#  Background:
#    Given I am on the home page
#    And I should see the "Features Items" heading
#
#  @smoke
#  Scenario: Valid User Login
#    When I navigate to the login page
#    Then I should see the "Login to your account" heading
#    When I log in with valid credentials
#    Then I should see the "Logout" link
#
#  @regression @smoke
#  Scenario: Invalid User Login
#    When I navigate to the login page
#    Then I should see the "Login to your account" heading
#    When I log in with invalid credentials
#    Then I should see the "Signup / Login" link

  @smoke
  Scenario: Failing test to verify screenshot capture
    Then I look for a non-existent heading to trigger a failure