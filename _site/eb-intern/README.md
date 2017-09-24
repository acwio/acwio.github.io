# Eventbrite: SimpleSearch
Eventbrite: SimpleSearch is a simple, concise interface for quickly searching through Eventbrite's event listing using 
the Eventbrite API.
 
## Quick Start
To start the project, navigate to the project directory and run `python manage.py runserver`. 

## Browsing: Categories
To use the SimpleSearch, a user should select 3 categories from the dropdown menus on the homepage of the application and 
click 'Search'. A user must select 3 categories in order for the search to take place. Additionally, each category should
be unique and should be a valid category. Automated validation has been implemented on both the front- and back-end of 
this application to ensure a user has an error-free experience.

## Browsing: All Events
In addition to browsing by category, a user may browse all events. To use this feature, a user should click "Browse all 
events" at the bottom of the homepage or the results page.

## UnitTests
UnitTests have been implemented for every possible scenario of acceptable and unacceptable input. To run this project's
 tests, navigate to the project directory and run: `python manage.py tests`
 
# List of Unit Tests
1. Validate request to Homepage / Index View
..* Expected Behavior: Render homepage. 
2. Validate request to /events/ without selected categories.
..* Expected Behavior: Render paginated listing of all events.
3. Validate request to /events/ without selected categories and a specific page number.
..* Expected Behavior: Render specified page of listing of all events.
3. Validate request to /events/ without selected categories and a page number that is not a number (NaN).
..* Expected Behavior: Render first page of listing of all events.
4. Validate request to /events/ with three valid categories.
..* Expected Behavior: Render paginated and filtered listing of all events. (HTTP Response 200)
5. Validate request /events/ with only two valid categories.
..* Expected Behavior: Render homepage / index with relevant error.
6. Validate request to /events/ with three valid categories, two of which are the same category.
..* Expected Behavior: Render homepage / index with relevant error.
7. Validate request to /events/ with three categories, one of which is invalid.
..* Expected Behavior: Render homepage / index with relevant error.
8. Validate request to 
 
## Author
Alex C. Williams [(https://github.com/csalexwilliams/)](https://github.com/csalexwilliams/)
