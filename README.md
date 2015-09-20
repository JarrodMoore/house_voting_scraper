# house_voting_scraper
Given a year this program compiles a csv of the U.S. House of Representatives votes.

The program uses the library of congress website to find the voting record for a given year, but does not include the roll call or the vote for speaker of the house in the final csv.

Command line arguments:
* year: The year whose data you want to download. Must be the last argument.
* --ignore_NP: The program does not write data for representatives who have any votes recorded as NP.
* --absTo5: Stores the value of present or not voting as .5.

The csv is set up as follows.
* First row: Name of the bill
* Firs column: Name of the representative
* 1: Voted in support
* 0: Voted against
* ABS/.5: Answered present or not voting
* NP: The representative is not on the page for the given vote

Python libraries used:
* requests
* itertools
* lxml
* time
* os
* argparse
