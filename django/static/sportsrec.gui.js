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

/**
 * Populates a submenu of the navigation bar
 * @param {string} header The header
 * @param {object} items An object representing the submenu items
 * @param {function} translator A function that translates an object item
 *                              into a text and href.
 * @returns {$.fn} Itself
 */
$.fn.populateSubmenu = function(header, items, translator) {
  var submenuHeader = $("<li/>").append($("<a/>", {text : header, href : "#"}));
  var submenu = $("<ul/>", {"class" : "submenu"});
  
  for (var item in items) {
    var info = translator(item, items);
    submenu.append($("<li/>").append(
          $("<a/>", {text : info.text, 
                     href : info.href, target : "_blank"})
    ));
  }
  
  this.append(submenuHeader.append(submenu));
  return this;
};

/** 
 * Populates the navigation bar
 */
$.fn.populateNavbar = function () {
  var menu = $("<ul/>", {"class" : "menu"});
  var menuTranslator = function(item, items) {
    var href = items[item].href;
    return {text : item, href : href};
  };
  
  menu.populateSubmenu("Navigation", sportsrec.menuitems, menuTranslator);
  menu.appendTo(this);
  return this;
}