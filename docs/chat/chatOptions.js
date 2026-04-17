/*OPTIONS*/
function changeTimestamps() {
  timeStampGlobal =!timeStampGlobal;
  var holder = document.getElementById("changeTimeStampStatus");

  if(timeStampGlobal) {
    holder.setAttribute("class","optionsStateOn");
    document.styleSheets[0].cssRules[0].style["opacity"] = 1;
  } else {
    holder.setAttribute("class","optionsStateOff");
    document.styleSheets[0].cssRules[0].style["opacity"] = 0;
  }
}

function splitBubbles() {
  splitBubbleGlobal = !splitBubbleGlobal;
  var holder = document.getElementById("splitBubblesStatus");

  if(splitBubbleGlobal) {
    traverseMe(true);
    holder.setAttribute("class","optionsStateOn");
  } else {
    traverseMe(false);
    holder.setAttribute("class","optionsStateOff");
  }
}

function alignBubblesF() {
  alignBubbles = !alignBubbles;
  var holder = document.getElementById("alignBubblesStatus");

  if(alignBubbles) {
    largeUpdate();
    holder.setAttribute("class","optionsStateOn");
  } else {
    largeUpdate();
    holder.setAttribute("class","optionsStateOff");
  }
}

function soundOffF() {
  soundNotifications = !soundNotifications;
  var holder = document.getElementById("soundNotificationsStatus");

  if(soundNotifications) {
    holder.setAttribute("class","optionsStateOn");
  } else {
    holder.setAttribute("class","optionsStateOff");
  }
}

function showImagesF() {
  showImagesOption = !showImagesOption;
  var holder = document.getElementById("showImagesStatus");

  if(showImagesOption) {
    holder.setAttribute("class","optionsStateOn");
  } else {
    holder.setAttribute("class","optionsStateOff");
  }
}

function traverseMe(direction) {
  var nodes = document.getElementById("transcript").childNodes;
  var element;
  var alias;
  var nameWidth = 0;
  var timeWidth = 0;
  var timeSpan;
  var nameSpan;
  var spacerWidth;
  var bubble;
  for(var loopA = 0, maxA = nodes.length; loopA < maxA; loopA++) {
    try {
      if(nodes[loopA].hasAttribute("me")) {
        element = nodes[loopA].childNodes;
        for(var loopB = 0, maxB = element.length; loopB < maxB; loopB++) {
          try {
            alias = element[loopB];
            switch(alias.getAttribute("class")) {
              case "grape":
              case "watermelon":
              case "tangerine":
              case "lime":
              case "blueberry":
                bubble = alias;
                break;
              case "nameSpan":
                nameWidth = alias.clientWidth;
                nameSpan = alias;
                break;
              case "timeSpan":
                timeWidth = alias.clientWidth;
                timeSpan = alias;
                break;
            }

          }
          catch(a) { }
        }

        spacerWidth = timeWidth;
        if(nameWidth > timeWidth) {
          spacerWidth = nameWidth;
        }

        if(spacerWidth > largestUser)
          largestUser = spacerWidth;

        if(direction) {
          //align to right
          timeSpan.style.left = "";
          timeSpan.style.right = "15px";
          nameSpan.style.left = "";
          nameSpan.style.right = "15px";
          bubble.style.left = "";
          if(alignBubbles)
            bubble.style.right = largestUser + 20 + "px";
          else
            bubble.style.right = spacerWidth + 20 + "px";
        } else {
          //align left
          timeSpan.style.right = "";
          timeSpan.style.left = "15px";
          nameSpan.style.right = "";
          nameSpan.style.left = "15px";
          bubble.style.right = "";
          bubble.style.left = spacerWidth + 20 + "px";
          if(alignBubbles)
            bubble.style.left = largestUser + 20 + "px";
          else
            bubble.style.left = spacerWidth + 20 + "px";
        }
      }
    } catch(a) { }
  }
}

function largeUpdate() {
  if(largestUser < 42)
    return;
  var nodes = document.getElementById("transcript").childNodes;
  var element;
  var alias;
  var nameWidth = 0;
  var timeWidth = 0;
  var timeSpan;
  var nameSpan;
  var spacerWidth;
  var bubble;
  for(var loopA = 0, maxA = nodes.length; loopA < maxA; loopA++) {
    try {
        element = nodes[loopA].childNodes;
        for(var loopB = 0, maxB = element.length; loopB < maxB; loopB++) {
          try {
            alias = element[loopB];
            switch(alias.getAttribute("class")) {
              case "grape":
              case "watermelon":
              case "tangerine":
              case "lime":
              case "blueberry":
                bubble = alias;
                break;
              case "nameSpan":
                nameWidth = alias.clientWidth;
                nameSpan = alias;
                break;
              case "timeSpan":
                timeWidth = alias.clientWidth;
                timeSpan = alias;
                break;
            }
          }
          catch(a) { }
        }
        spacerWidth = timeWidth;
        if(nameWidth > timeWidth) {
          spacerWidth = nameWidth;
        }

        if(bubble.style.left == "") {
          if(alignBubbles)
            bubble.style.right = largestUser + 20 + "px";
          else
            bubble.style.right = spacerWidth + 20 + "px";
        } else {
          if(alignBubbles)
            bubble.style.left = largestUser + 20 + "px";
          else
            bubble.style.left = spacerWidth + 20 + "px";
        }

    } catch(a) {}
  }
}

/*END OPTIONS*/

