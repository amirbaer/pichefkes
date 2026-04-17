/*CHAT METHODS*/
function send_message() {
  var message = document.getElementById("message").value;

  // Send only non-empty messages and send them only when connected to server
  if(message != "" && socket.socket.open) {
    document.getElementById("message").value = "";

    var result = parseMessage(message)
    var parsed_message = result[0];

    if(result[1].length != 0) {
      handleYoutube(result, true, global_user_name, global_user_id);
    } else {
      createBubble(global_user_name, global_user_id, parsed_message, true);
    }

    if(message.length > max_text) {
      message = "The message was too large to send.";
      createBubble(global_user_name, global_user_id, message, true);
    } else {
      var ct_message = sjcl.encrypt(window.password, message);
      socket.emit('message', ct_message);
    }
    scrollToBottom();
  }
}

// Decodes escaped html text back into unescaped html text
function htmlDecode(input) {
  var e = document.createElement('div');
  e.innerHTML = input;
  return e.childNodes.length === 0 ? "" : e.childNodes[0].nodeValue;
}

// parses given text for URLs and converts them to hyperlinks
function parseMessage(message) {
  var ytEmbed = new Array();

  parsed_message = message.replace(urlRegex, function(url) {
    var httpRegex = /^https?:\/\//;

    // Parsing for youtube embeds
    if(url.indexOf("youtube.com/watch") != -1) {
      var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
      var match = url.match(regExp);
      if (match&&match[7].length==11){
        var front = "<div style = 'margin-top: -15px;margin-bottom: 10px;margin-left: 35px; box-shadow: 0px 0px 10px black;height: 315px;width: 560px;' id = 'frame'><object width=\"480\" height=\"360\"><param name=\"movie\"value=\"https://www.youtube.com/v/";
        var middle = "?version=3&autohide=1&showinfo=0&modestbranding=1\"></param><param name=\"allowScriptAccess\" value=\"always\"></param><embed src=\"https://www.youtube.com/v/";
        var tail = "?version=3&autohide=1&showinfo=0&modestbranding=1\"type=\"application/x-shockwave-flash\"allowscriptaccess=\"always\"width=\"560\" height=\"315\"></embed></object></div>";
        //ytEmbed.push(front + match[7] + middle + match[7] + tail);
        //return front + match[7] + middle + match[7] + tail;
        ytEmbed.push(url);
        return url;
      } else {
        return url;
      }
    }

    // Parsing for url embeds
    if(httpRegex.test(url)) {
      return '<a target="_blank" href="' + url + '">' + url + '</a>';
    } else {
      return '<a target="_blank" href="http://' + url + '">' + url + '</a>';
    }
  });

  return [parsed_message, ytEmbed];
}

function handleYoutube(data, me, user, unique_id) {
  var start = 0;
  var oldStart;

  for(var loopA = 0, maxA = data[1].length; loopA < maxA; loopA++) {
    oldStart = start;
    start = data[0].indexOf(data[1][loopA],start) + data[1][loopA].length;

    //Convert to url
    var ytHtml = data[1][loopA].replace(urlRegex, function(url) {
      var httpRegex = /^https?:\/\//;
        if(httpRegex.test(url)) {
          return '<a target="_blank" href="' + url + '">' + url + '</a>';
        } else {
          return '<a target="_blank" href="http://' + url + '">' + url + '</a>';
        }
    });

    createBubble(user, unique_id, data[0].substring(oldStart, start - data[1][loopA].length) + ytHtml, me);

    var ytEmbed = document.createElement("div");
    ytEmbed.setAttribute("class","ytEmbed");

    //Get youtube id
    var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
    var match = data[1][loopA].match(regExp);
    var ytId = "";
    if (match&&match[7].length==11){
      ytId = match[7];
    }

    if(ytId != "") {
      var front = "<div style ='margin-left: auto; margin-right: auto;height: 315px;width: 560px;' id = 'frame'><object width=\"480\" height=\"360\"><param name=\"movie\"value=\"https://www.youtube.com/v/";
      var front = "<div class = '" + roomData[unique_id]["color"] + "Yt' style ='margin-left: auto; margin-right: auto; box-shadow: 0px 0px 10px black;height: 315px;width: 560px;' id = 'frame'><object width=\"480\" height=\"360\"><param name=\"movie\"value=\"https://www.youtube.com/v/";
      var middle = "?version=3&autohide=1&showinfo=0&modestbranding=1\"></param><param name=\"allowScriptAccess\" value=\"always\"></param><embed src=\"https://www.youtube.com/v/";
      var tail = "?version=3&autohide=1&showinfo=0&modestbranding=1\"type=\"application/x-shockwave-flash\"allowscriptaccess=\"always\"width=\"560\" height=\"315\"></embed></object></div>";

      ytEmbed.innerHTML = front + ytId + middle + ytId + tail;

      document.getElementById('transcript').appendChild(ytEmbed);
    }
  }

  //Create remainder if present
  if(start != data[0].length - 1) {
    var temp = data[0].substring(start);
    if(temp.length != 0)
      createBubble(user, unique_id, temp, me);
  }
}

// Send true if focus is given to ChatStep, false if focus is lost
function sendActive(focus) {
  socket.emit('status', {"active": focus});
}

// Send true if user starts typing, false if they stop typing
function sendTyping(startTyping) {
  socket.emit('status', {"active": hasFocus, "typing": startTyping});
}

//me is boolean if message sent by me or not
function createBubble(nick, unique, body, me) {

  var holder = document.getElementById("transcript");

  var bubbleFrame = document.createElement("div");
  bubbleFrame.setAttribute("class","bubbleFrame");

  var bubble = document.createElement("div");
  bubble.setAttribute("class", roomData[unique]["color"]);

  var bubbleBody = document.createElement("span");
  bubbleBody.setAttribute("class","bubbleBody");
  bubbleBody.innerHTML = body;

  bubble.appendChild(bubbleBody);

  bubbleFrame.appendChild(bubble);

  var nameSpan = document.createElement("span");
  nameSpan.setAttribute("class","nameSpan");
  nameSpan.appendChild(document.createTextNode(htmlDecode(nick)));
  bubbleFrame.appendChild(nameSpan);

  var timeSpan = document.createElement("span");
  timeSpan.setAttribute("class","timeSpan");

  var timeObj = new Date();

  var hours = timeObj.getHours();
  //Check AM/PM
  var amOrPm = " am";
  if(hours > 12) {
    hours = hours - 12;
    amOrPm = " pm";
  }

  if(hours == 0)
    hours = 12;

  var min = timeObj.getMinutes();
  if(min < 10)
    min = "0" + min;
  timeSpan.appendChild(document.createTextNode(hours + ":" + min + amOrPm));
  bubbleFrame.appendChild(timeSpan);

  SYSTEM.id++;
  bubbleFrame.setAttribute("id",SYSTEM.id + 'F');

  holder.appendChild(bubbleFrame);

  //Resize bubble based on width size
  if(bubble.clientWidth > 300) {
    bubble.style.width = "300px";
  }

  if(splitBubbleGlobal && me) {
    //align to right
    var nameWidth = nameSpan.clientWidth;
    var timeWidth = timeSpan.clientWidth;
    var spacerWidth = timeWidth;
    if(nameWidth > timeWidth) {
      spacerWidth = nameWidth;
    }
    if(spacerWidth > 125)
      spacerWidth = 125;

    timeSpan.style.right = "15px";
    nameSpan.style.right = "15px";

    if(spacerWidth > largestUser)
      largestUser = spacerWidth;

    if(alignBubbles)
      bubble.style.right = largestUser + 20 + "px";
    else
      bubble.style.right = spacerWidth + 20 + "px";

    bubbleFrame.style.height = bubble.clientHeight + 10 + "px";
  } else {
    //align to left
    var nameWidth = nameSpan.clientWidth;
    var timeWidth = timeSpan.clientWidth;
    var spacerWidth = timeWidth;
    if(nameWidth > timeWidth) {
      spacerWidth = nameWidth;
    }
    if(spacerWidth > 125)
      spacerWidth = 125;

    timeSpan.style.left = "15px";
    nameSpan.style.left = "15px";

    if(spacerWidth > largestUser)
      largestUser = spacerWidth;

    if(alignBubbles)
      bubble.style.left = largestUser + 20 + "px";
    else
      bubble.style.left = spacerWidth + 20 + "px";

    bubbleFrame.style.height = bubble.clientHeight + 10 + "px";
  }

  //add me attribute
  if(me) {
    bubbleFrame.setAttribute("me","me");
  }

  fade(SYSTEM.id + 'F',0, 20);
}
/*END CHAT METHODS*/
