/**
 * CITS2232 Project 2013 GUI stuff.
 */

sportsrec = {};

sportsrec.menuitems = {
  "Clubs" : {href : "clubs/"},
  "Members" : {href : "members/"},
  "Stats" : {href : "stats/"}
};

/**
 * Writes the current date to wherever it's called.
 */
function getDate(){
	document.write((new Date()).toDateString());
}
