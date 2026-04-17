try {
  if(config_devMode) var socket = io.connect("http://"+hostname);
  else var socket = io.connect("https://"+hostname);
}
catch(err) {
  console.log("io.connect error");
  alert("Cannot connect to server. It's either down or blocked by your firewall, sorry. Some workplace firewalls block the port Chatstep runs on (https).");
}

/*All globals*/
var BROWSERINFO = new Object();
var TIME = new Object();
var BROWSER = new Object();
var SYSTEM = new Object();
var SYSTEM = new Object();
var ANIMATE = new Object();

//Chat related globals
var max_file = 750000; // This check is also done server-side.
var max_text = 2000; // This check also occurs server-side.
window.password = "";
var room = "";
var global_user_name = "";
var global_user_id = -1;
var global_room_name = "";
var global_room_hash = "";
var global_auto_create = false;
var pass_room_hash = "";

// Regex to parse URLs
var urlRegex = /[-a-z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-z0-9@:%_\+.~#?&\/\/=]*)?/gi;

//Color Variables for bubbles
var allColors = ["grape","watermelon","tangerine","lime","blueberry"];
var roomData = new Object();

//Chat Option globals
var timeStampGlobal = false; //TimeStampOption Global
var splitBubbleGlobal = true; //SplitBubble option Global
var soundNotifications = true; //SoundNotifications option Global
var alignBubbles = true; //Aligned Global
var showImagesOption = true; //Show Images option global
var largestUser = 0;

// Maintain knowledge of focus on window to show unread messages
var unread = 0;
var active_element;
var hasFocus = true;
var isTyping = false; // user is currently typing a message
var transcriptExtra = false;
/*END GLOBALS*/

window.onblur = function()  { onWindowBlur(); }
window.onfocus = function() { onWindowFocus(); }
window.onload = start;

function start() {
  /*check url to see if room is defined ex. "https://chatstep.com/#testRoom"
    focus roomName field if NOT defined
    focus nickName field if defined
  */

  /*
  if(window.location.hash != "") {
    document.getElementById("room").value = window.location.hash.substring(1);
    document.getElementById("nickname").focus();
  }
  else {
    document.getElementById("room").focus();
  }*/
//---------------------------------------------------------------


/*setup BROWSERINFO global variable -------------------------------------*/

  //get browser type
  if (navigator.userAgent.toLowerCase().indexOf("firefox") > -1) {
    BROWSERINFO.type = "firefox";
  }
  else if (navigator.userAgent.toLowerCase().indexOf("chrome") > -1) {

    BROWSERINFO.type = "chrome";
  }
  else if (navigator.userAgent.toLowerCase().indexOf("msie") > -1) {
    BROWSERINFO.type = "msie";
    alert("ChatStep is currently not supported in Internet Expolorer");
  }
  else if (navigator.userAgent.toLowerCase().indexOf("safari") > -1) {

    BROWSERINFO.type = "safari";
  }
  else {
    BROWSERINFO.type = "???";
  }

  //get css selector
  if(document.all) {
    BROWSERINFO.css = 'rules';
  }
  else {
    BROWSERINFO.css = 'cssRules';
  }

//---------------------------------------------------------------
  //Setup Glow borders based on screen width
  var winW = window.innerWidth;
  halfW = winW/2;
  var colors = ["lightPink","lightSalmon","orange","lightGreen","lightBlue"];
  var max = parseInt(winW/200);
  var loopA = 0;
  /*
  for(; loopA < max; loopA++) {
    var bottom = document.createElement("div");
    var currentColor = colors.pop();
    bottom.setAttribute("class","mainTitleBar");
    bottom.setAttribute("id","mainTitleBar" + loopA);
    bottom.style.boxShadow = "0px 0px 15px 10px " + currentColor;
    bottom.style.left = loopA*200 +"px";
    colors.unshift(currentColor);
    document.getElementById("barholder").appendChild(bottom);
    //document.body.appendChild(bottom);
  }

  var bottom = document.createElement("div");
  var currentColor = colors.pop();
  bottom.setAttribute("class","mainTitleBar");
  bottom.setAttribute("id","mainTitleBar" + loopA);
  bottom.style.boxShadow = "0px 0px 15px 10px " + currentColor;
  bottom.style.left = (max)*200 + "px";
  bottom.style.width =  (winW%200) + "px";
  colors.unshift(currentColor);
  document.body.appendChild(bottom);
  */
  
  //document.getElementById("authors").style.left = ((((halfW - Math.abs(200))/winW)*100).toFixed(2)) + "%";
  //document.getElementById("emails").style.left = ((((halfW - Math.abs(200))/winW)*100).toFixed(2)) + "%";

  var upload_box = document.body;
  var winW = window.innerWidth;
  var winH = window.innerHeight;
  var halfW = winW/2;
  document.getElementById("mainBox").style.left = ((((halfW - Math.abs(400))/winW)*100).toFixed(2)) + "%";

  upload_box.addEventListener("dragenter", dragEnter, false);
  upload_box.addEventListener("dragexit", dragExit, false);
  upload_box.addEventListener("dragover", dragOver, false);
  upload_box.addEventListener("drop", drop, false);
  resizeDelay();

}
