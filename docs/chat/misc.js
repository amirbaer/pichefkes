SYSTEM.id = 0;
var OVERLAY = {
  donate:'<div id = "donateClose"><span id = "donateCloseText" onclick = "hideDonateBubble()">X</span></div><span id = "donateBubbleText">Thank you for supporting our site. Please copy this address into your bitcoin client.</span><span id = "donateAddress">1LNgLBuPJKEpHkQS4noG6J6KpJscvAdUbZ</span>',
  share:'<div id = "donateClose"><div id = "shareTitle">Share this room: </div><div id = "shareURL"></div><div id = "shareTwitter"><img id = "shareOnTwitterIcon" src = "image/twitter24.png"></img><a style = "color: whiteSmoke;text-decoration: none;position: relative;top: -6px;left: 6px;"target="_blank" id = "shareOnTwitter">Share on Twitter</a></div><span id = "donateCloseText" onclick = "hideShareButton()">X</span></div>'
};


function resizeDelay() {
  //Get width
  //fix userlist at 150
  //transcript at 500
  //padding 50 left and right
  var winW, winH;
  if(BROWSER.name) {
    winW = window.innerWidth;
    winH = window.innerHeight;
  }
  else {
    winW = document.documentElement.clientWidth;
    winH = document.documentElement.clientHeight;
  }

  var transcript = document.getElementById("transcript");
  var userList = document.getElementById("userlist");
  var message = document.getElementById("message");

  //Check if meets minimum
  var minX = winW - 750;
  var minY = winH - 500;

  //WidthCheck
  if(minX > 0) {
    transcript.style.width = minX + 500 + "px";
    message.style.width = minX + 510 + "px";
  }
  else {

  }
  //Height Check
  if(minY > 0) {
    if(transcriptExtra) {
      transcript.style.height = minY + 370 + "px";
      transcript.style.top ="0px";
    }
    else {
      transcript.style.height = minY + 320 + "px";
    }
    //userList.style.height = 200 + "px";
    //message.style.top = minY + 405 + 15 + "px";
  }

  /*RIGHT PANEL*/
  //Adjust height And width of Right panel
  var transcriptH = parseInt(transcript.style.height)/2;
  document.getElementById("userlistFrame").style.height = transcriptH -50 + "px";
  //document.getElementById("optionsFrame").style.top = transcriptH + 45 - 15 + "px";
  //document.getElementById("optionsFrame").style.height = transcriptH + 45+ "px";

  document.getElementById("fog").style.width = winW + "px";


  //Center Login if present
  var halfW = winW/2;
  var halfH = winH/2;
  //var promptHolder = document.getElementById("prompt");
  //promptHolder.style.left = ((((halfW - Math.abs(112))/winW)*100).toFixed(2)) + "px";
  try {
    document.getElementById("mainBox").style.left = ((((halfW - Math.abs(400))/winW)*100).toFixed(2)) + "%";
    document.getElementById("mainBox").style.top = ((((halfH - Math.abs(195))/winH)*100).toFixed(2)) + "%";
  }
  catch(a) {

  }

}

function showShareBubble() {
  //var transcriptH = parseInt(transcript.style.height) - parseInt(document.getElementById("optionsFrame").style.height) *.315;
  var transcriptH = parseInt(transcript.style.height) - 160 *.315;
  var donateBubble = document.getElementById("donateBubble");
  donateBubble.innerHTML = OVERLAY.share;
  donateBubble.style.zIndex = 20;
  donateBubble.style.opacity = 1;
  donateBubble.style.top = transcriptH + 'px';

  /*
  var donateTail = document.getElementById("donateTail");
  donateTail.style.zIndex = 20;
  donateTail.style.opacity = 1;
  donateTail.style.top = transcriptH + 'px';
  */

  document.getElementById("shareURL").innerHTML = "www.chatstep.com/" + window.location.hash;
  document.getElementById("shareOnTwitter").setAttribute("href",'https://twitter.com/intent/tweet?text=Chat%20with%20me%20right%20now%20at%20https://chatstep.com/%23' + global_room_name + '%20!');
  document.getElementById("shareOnTwitterIcon").setAttribute("onclick",'window.open("https://twitter.com/intent/tweet?text=Chat%20with%20me%20right%20now%20at%20https://chatstep.com/%23' + global_room_name + '%20!")');

}

function hideShareButton() {

  var donateBubble = document.getElementById("donateBubble");
  donateBubble.style.zIndex = -1;
  donateBubble.style.opacity = 0;

  // var donateTail = document.getElementById("donateTail");
  // donateTail.style.zIndex = -1;
  // donateTail.style.opacity = 0;

  donateBubble.innerHTML = "";


}

function showDonateBubble() {
  var transcriptH = parseInt(transcript.style.height) - 30;
  var donateBubble = document.getElementById("donateBubble");
  donateBubble.innerHTML = OVERLAY.donate;
  donateBubble.style.zIndex = 20;
  donateBubble.style.opacity = 1;
  donateBubble.style.top = transcriptH + 'px';

  // var donateTail = document.getElementById("donateTail");
  // donateTail.style.zIndex = 20;
  // donateTail.style.opacity = 1;
  // donateTail.style.top = transcriptH + 'px';
}

function hideDonateBubble() {

  var donateBubble = document.getElementById("donateBubble");
  donateBubble.style.zIndex = -1;
  donateBubble.style.opacity = 0;

  var donateTail = document.getElementById("donateTail");
  donateTail.style.zIndex = -1;
  donateTail.style.opacity = 0;

  donateBubble.innerHTML = "";
}


window.onresize = function(){
  clearTimeout(SYSTEM.resize);
  SYSTEM.resize = setTimeout("resizeDelay()",10);
}

function deletePrompt() {
    /*
  //var body = document.body;
  var div = document.getElementById("prompt");
  //body.removeChild(div);
  div.parentNode.removeChild(div);
  console.log(div);
  //console.log(body)
  */
}

function initOverlay(type) {

  //Hide mainTitle
  document.getElementById("mainTitle").style.opacity = 0;

  //show overlay skeleton
  var overlayHolder = document.getElementById("overlay");
  overlayHolder.style.opacity = 1;
  overlayHolder.style.zIndex = 20;

  overlayHolder.innerHTML = OVERLAY[type];
}

/*DRAG*/
function stopEvents(evt) {
  evt.stopPropagation();
  evt.preventDefault();
}

function dragEnter(evt) {
  stopEvents(evt);
}

function dragExit(evt) {
  stopEvents(evt);
}

function dragOver(evt) {
  stopEvents(evt);
}

function drop(evt) {
  stopEvents(evt);

  var files = evt.dataTransfer.files;
  var num_files = files.length;

  if (num_files > 0)
    handleFiles(files);
}

// File upload original method written using Riyad Kalla's tutorial
function handleFiles(files) {
  for(var i = 0; i < files.length && i < 5; i++) {
    var cur_file = files[i];
    window.cur_file_name = cur_file.name;
    window.reader = new FileReader();

    window.reader.onprogress = handleReaderProgress;
    window.reader.onloadend = handleReaderLoadEnd;
    window.reader.readAsDataURL(cur_file);
  }
}

function handleReaderProgress(evt) {
  if (evt.lengthComputable) {
    //console.log(evt.loaded);
    //var loaded = (evt.loaded / evt.total);
    //$("#progressbar").progressbar({ value: loaded * 100 });
  }
}

function handleReaderLoadEnd(evt) {
  // Append file to page.
  if(evt.target.result.length > max_file) {
    document.getElementById('transcript').innerHTML += "<div class='rec_message'>This file was too large to send.</div>";
    scrollToBottom();
  }
  else {
    var color = roomData[global_user_id]["color"] + "Yt";
    // Set max local image width as a percent of window width
    var max_width = 0.75 * window.innerWidth;
    document.getElementById('transcript').innerHTML += "<div class='rec_message'><img class ='" + color + "' OnLoad='scrollToBottom();' style='max-width: " + max_width +
      "' src='" + evt.target.result + "' /></div>";
    var ct_file = sjcl.encrypt(window.password, evt.target.result);
    socket.emit('file', ct_file);
  }
}

/*DEBUG*/
function debugAlert(data) {
  if(development) alert(data);
}
/*END DEBUG*/
