# house_voting_scraper
Given a year this program compiles a csv of the House of Representatives votes.

The first row is the name of the bill voted on and the first column is the name of the representative. '1' represents a yea vote, '0' a nay vote, and '.5' abstaining. 

This program does not include the roll call and the vote for speaker of the house in the final csv.

If a representative is not present during the roll call, they will not be represented in the final csv.

Python libraries used:
* requests
* itertools
* lxml
* time
