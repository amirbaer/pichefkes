var optionNum = 1;
var selected = -1;
var pollObj = new Object();
var pollTimeLeft;
var voteMessage;
var createPollOpen = false;

var blueberryBar = "rgba(152, 176, 217, 1)";
var grapeBar = "rgba(233,60,236,1)";
var watermelonBar = "rgb(254,187,187)";
var limeBar = "rgb(205,235,142)";
var tangerineBar = "rgb(255,214,94)";

var bar = {
  blueberry: blueberryBar,
  grape: grapeBar,
  watermelon: watermelonBar,
  lime: limeBar,
  tangerine: tangerineBar
};





var blueberry  = "background: #C3D9FF;background: -moz-linear-gradient(top, rgba(195, 217, 255, 1) 0%, rgba(177, 200, 239, 1) 41%, rgba(152, 176, 217, 1) 100%);\background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(195, 217, 255, 1)), color-stop(41%,rgba(177, 200, 239, 1)), color-stop(100%,rgba(152, 176, 217, 1)));background: -webkit-linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);background: -o-linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);background: -ms-linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);background: linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);box-shadow: 0px 0px 5px #C3D9FF;";
var grape      = "background: rgb(235,233,249);background: -moz-linear-gradient(top, rgba(235,233,249,1) 0%, rgba(216,208,239,1) 50%, rgba(206,199,236,1) 51%, rgba(193,191,234,1) 100%);background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(235,233,249,1)), color-stop(50%,rgba(216,208,239,1)), color-stop(51%,rgba(206,199,236,1)), color-stop(100%,rgba(193,191,234,1))); background: -webkit-linear-gradient(top, rgba(235,233,249,1) 0%,rgba(216,208,239,1) 50%,rgba(206,199,236,1) 51%,rgba(193,191,234,1) 100%); background: -o-linear-gradient(top, rgba(235,233,249,1) 0%,rgba(216,208,239,1) 50%,rgba(206,199,236,1) 51%,rgba(193,191,234,1) 100%);background: -ms-linear-gradient(top, rgba(235,233,249,1) 0%,rgba(216,208,239,1) 50%,rgba(206,199,236,1) 51%,rgba(193,191,234,1) 100%);background: linear-gradient(top, rgba(235,233,249,1) 0%,rgba(216,208,239,1) 50%,rgba(206,199,236,1) 51%,rgba(193,191,234,1) 100%);box-shadow: 0px 0px 5px rgb(235,233,249);";
var watermelon = "background: rgb(254,187,187);background: -moz-linear-gradient(top, rgba(254,187,187,1) 0%, rgba(254,144,144,1) 45%, rgba(255,92,92,1) 100%);background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(254,187,187,1)), color-stop(45%,rgba(254,144,144,1)), color-stop(100%,rgba(255,92,92,1)));background: -webkit-linear-gradient(top, rgba(254,187,187,1) 0%,rgba(254,144,144,1) 45%,rgba(255,92,92,1) 100%);background: -o-linear-gradient(top, rgba(254,187,187,1) 0%,rgba(254,144,144,1) 45%,rgba(255,92,92,1) 100%);background: -ms-linear-gradient(top, rgba(254,187,187,1) 0%,rgba(254,144,144,1) 45%,rgba(255,92,92,1) 100%);background: linear-gradient(top, rgba(254,187,187,1) 0%,rgba(254,144,144,1) 45%,rgba(255,92,92,1) 100%);box-shadow: 0px 0px 5px rgb(254,187,187);";
var lime       = "background: rgb(205,235,142);background: -moz-linear-gradient(top,  rgba(205,235,142,1) 0%, rgba(165,201,86,1) 100%);background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(205,235,142,1)), color-stop(100%,rgba(165,201,86,1)));background: -webkit-linear-gradient(top,  rgba(205,235,142,1) 0%,rgba(165,201,86,1) 100%);background: -o-linear-gradient(top,  rgba(205,235,142,1) 0%,rgba(165,201,86,1) 100%); background: -ms-linear-gradient(top,  rgba(205,235,142,1) 0%,rgba(165,201,86,1) 100%);background: linear-gradient(top,  rgba(205,235,142,1) 0%,rgba(165,201,86,1) 100%);filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#cdeb8e', endColorstr='#a5c956',GradientType=0 );box-shadow: 0px 0px 5px rgb(205,235,142);";
var tangerine  = "background: rgb(255,214,94);background: -moz-linear-gradient(top, rgba(255,214,94,1) 0%, rgba(254,191,4,1) 100%);background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(255,214,94,1)), color-stop(100%,rgba(254,191,4,1)));background: -webkit-linear-gradient(top, rgba(255,214,94,1) 0%,rgba(254,191,4,1) 100%);background: -o-linear-gradient(top, rgba(255,214,94,1) 0%,rgba(254,191,4,1) 100%); background: -ms-linear-gradient(top, rgba(255,214,94,1) 0%,rgba(254,191,4,1) 100%); background: linear-gradient(top, rgba(255,214,94,1) 0%,rgba(254,191,4,1) 100%);box-shadow: 0px 0px 5px rgb(255,214,94);";

var colors = {
  blueberry: blueberry,
  grape: grape,
  watermelon: watermelon,
  lime: lime,
  tangerine: tangerine
};

function showPollForm() {
  if(createPollOpen) {
    hideShareButton();
    createPollOpen = false;
    return;
  }
  createPollOpen = true;


  optionNum = 1;

  var transcriptH = parseInt(transcript.style.height) - parseInt(document.getElementById("optionsFrame").style.height) *.125;

  var donateTail = document.getElementById("donateTail");
  donateTail.style.zIndex = 20;
  donateTail.style.opacity = 1;
  donateTail.style.top = transcriptH + 'px';

  var donateBubble = document.getElementById("donateBubble");
  donateBubble.innerHTML = "<div id='donateClose'><span id='donateCloseText' onclick='hideShareButton()'>X</span></div><div class = 'pollFormTitle' id = 'title'>Create New Poll</div><input type = 'text' id = 'pollFormNameField' class = 'pollFormField' placeholder = 'Poll Question'></input><div id = 'seperator'></div><div id = 'pollFormOptionsScroll'><div id = 'pollFormOptionsAll'></div></div><div id = 'pollFormOptionsBottom'><input id = 'pollFormDoneOption' type = 'button' value = 'Done'onclick = 'createPollDone()' ></input><input id = 'pollFormAddOption'  onclick = 'addOption()' type = 'button' value = 'Add Option'></input></div><select id = 'pollTimeSelect'><option value=5>5 Seconds</option><option value=30>30 Seconds</option><option value=60>1 Minute</option><option value=120>2 Minutes</option><option value=300>5 Minutes</option></select>";
  donateBubble.style.zIndex = 20;
  donateBubble.style.opacity = 1;
  donateBubble.style.top = transcriptH - 230 + 'px';
  donateBubble.style.height = "300px";

  document.getElementById("pollFormNameField").style.top = "55px";
  document.getElementById("pollFormNameField").style.width = "220px";
  document.getElementById("pollFormNameField").style.left = "80px";

  addOption();
  addOption();

}

function addOption() {

  var pollFormOption = document.createElement("div");
  pollFormOption.setAttribute("class","pollFormOption");

  var pollFormOptionRadio = document.createElement("input");
  pollFormOptionRadio.setAttribute("type", "radio");
  pollFormOptionRadio.setAttribute("disabled", true);
  pollFormOptionRadio.setAttribute("class","pollFormOptionRadio");

  var pollFormOptionInput = document.createElement("input");
  pollFormOptionInput.setAttribute("type", "text");
  pollFormOptionInput.setAttribute("class", "pollFormOptionInput");
  pollFormOptionInput.setAttribute("placeholder", "Poll Option " + optionNum.toString());
  pollFormOptionInput.setAttribute("onkeydown","if (event.keyCode == 13) { createPollDone(); }");

  pollFormOption.appendChild(pollFormOptionRadio);
  pollFormOption.appendChild(pollFormOptionInput);

  document.getElementById("pollFormOptionsAll").style.height = optionNum*30 + "px";
  document.getElementById("pollFormOptionsAll").appendChild(pollFormOption);
  optionNum++;
  document.getElementById('pollFormOptionsScroll').scrollTop = 9999999;

}

function createPollDone() {
  //Verify existing form, and build objects if ok
  var pollFormNameField = document.getElementById("pollFormNameField").value;
  if(pollFormNameField != "") {
    pollObj.question = pollFormNameField;
    pollObj.options = new Array();
    var children = document.getElementById("pollFormOptionsAll").childNodes;
    for(var loop = 0; loop < children.length; loop++) {
      if(children[loop].childNodes[1].value == "") {
      }
      else {
        pollObj.options.push(children[loop].childNodes[1].value);
      }
    }

    pollObj.time = document.getElementById("pollTimeSelect").value;

    socket.emit('poll_request', pollObj);
    var doneButton = document.getElementById("pollFormDoneOption");
    doneButton.setAttribute("id","pollFormDoneImage");
  }
  else {
    return;
  }
}


// Handle reply from server on attempt to create a poll
socket.on('poll_reply', function (data) {
  try {
    if(data.success) {
      //Close the modal
      var createPollBubble = document.getElementById("donateBubble");
      createPollBubble.innerHTML = "";
      createPollBubble.style.zIndex = -1;
      createPollBubble.style.opacity = 0;

      var createPollTail = document.getElementById("donateTail");
      createPollTail.style.zIndex = -1;
      createPollTail.style.opacity = 0;
    }
    else {
      alert("Unable to create poll, there is already one in session");
      var doneButton = document.getElementById("pollFormDoneImage");
      doneButton.setAttribute("id","pollFormDoneOption");
    }
  }
  catch (err) {
    console.log(err);
  }
});

// Handle reply from server on attempt to vote
socket.on('vote_reply', function (data) {
  try {
    // use in future to do loading gif on vote button
    console.log(data);
  } catch (err) {
    console.log(err);
  }
});

// Handle broadcasted results of a poll from the server
socket.on('poll_results', function (data) {
  try {
    var results_str =
      "These options: " +
      data.winners +
      " won with " +
      data.winner_votes +
      " votes each, out of " +
      data.total_count +
      " total votes.";
      // + "Poll created by: " +
      //data.creator_id;

    var color = roomData[data.unique]["color"] + "Yt";
    document.getElementById("transcript").innerHTML += "<div class='rec_message'><span class ='" + color +
                            "' style='max-width: " + 300 +
                            "px;'> " + results_str + "<span /></div>";
    scrollToBottom();
  } catch (err) {
    console.log(err);
  }
});



/*POLL VIEW RELATED METHODS--------------------------------------------------------------------------*/
var viewPollNum;

socket.on('new_poll', function (data) {
  try {
    //Go into view mode
    viewPollNum = 0;
    selected = -1;
    pollObj = new Object();

    pollObj.originalWidth = parseFloat(document.getElementById("transcript").style.width);
    pollObj.toWidth = pollObj.originalWidth - 200;

    document.getElementById("userlistFrame").style.right = "0px";
    document.getElementById("userlistFrame").style.top = "0px";

    var pollHolder = document.createElement("div");
    pollHolder.setAttribute("id", "pollHolder");
    pollHolder.setAttribute("onmouseover", "pollViewHover(this)");

    var pollTitle = document.createElement("div");
    pollTitle.appendChild(document.createTextNode("Poll: " + data.question));
    pollTitle.setAttribute("id", "pollTitle");
    pollTitle.setAttribute("style",colors[roomData[data.creator_id]["color"]]);

    var pollFormOptionsScrollB = document.createElement("div");
    pollFormOptionsScrollB.setAttribute("id", "pollViewFormOptionsScroll");

    var pollFormOptionsAllB = document.createElement("div");
    pollFormOptionsAllB.setAttribute("id", "pollViewFormOptionsAll");

    var pollViewFormOptionsLip = document.createElement("div");
    pollViewFormOptionsLip.setAttribute("id","pollViewFormOptionsLip");
    pollTimeLeft = data.max_time;


    pollFormOptionsScrollB.appendChild(pollFormOptionsAllB);

    pollHolder.appendChild(pollTitle);
    pollHolder.appendChild(pollFormOptionsScrollB);
    pollHolder.appendChild(pollViewFormOptionsLip);

    document.body.appendChild(pollHolder);

    document.getElementById("pollViewFormOptionsAll").style.height = (data.options.length + 1)*34 + "px";

    pollObj.top = 0;

    //Cap Scroll at 200
    if(data.options.length*34 < 200) {
      document.getElementById("pollViewFormOptionsScroll").style.height = (data.options.length + 1)*34 + "px";
      pollObj.top = 70 + 40 + 45 + parseInt((data.options.length + 1)*34);
    }
    else {
      document.getElementById("pollViewFormOptionsScroll").style.height = "200px";
      pollObj.top = 70 + 40 + 45 + 200;
    }

    createPollViewOption("Abstain from voting",data.creator_id);

    for(var loop = 0; loop < data.options.length; loop++) {
      createPollViewOption(data.options[loop],data.creator_id );
    }


    animateIntoVoteView(0);
    createPollOpen = false;

  } catch (err) {
    console.log(err);
  }
});

function createPollViewOption(question, uiud) {
  var option;
  if((viewPollNum%2)== 0) {
    option = "<div class = 'pollViewFormOptionA' onmouseover = 'pollViewHover(this)'onclick = 'castVote(" + viewPollNum + ")' ><div id = " + "option" + viewPollNum +  " class = 'pollViewFormOptionNotSelected' onclick = 'castVote(" + viewPollNum + ")' onmouseover = 'pollViewHover(this)' ></div><div onmouseover = 'pollViewHover(this)' onclick = 'castVote(" + viewPollNum + ")' class = 'pollViewFormOptionText'>" + question + "</div></div>";
  }
  else {
    option = "<div class = 'pollViewFormOptionB' onmouseover = 'pollViewHover(this)' onclick = 'castVote(" + viewPollNum + ")'><div id = " + "option" + viewPollNum +  " onmouseover = 'pollViewHover(this)' class = 'pollViewFormOptionNotSelected' onclick = 'castVote(" + viewPollNum + ")' ></div><div onmouseover = 'pollViewHover(this)' onclick = 'castVote(" + viewPollNum + ")' class = 'pollViewFormOptionText'>" + question + "</div></div>";
  }
//pollTitle.setAttribute("style",colors[roomData[data.creator_id]["color"]]);

  document.getElementById("pollViewFormOptionsAll").innerHTML += option;
  document.getElementById("option" + viewPollNum).setAttribute("style",colors[roomData[uiud]["color"]]);
  viewPollNum++;
}

function pollViewHover(a) {

  //Reset old
  var holder = document.getElementById("pollViewFormOptionsAll").childNodes;

  for(var loop = 0; loop < holder.length; loop++) {
    if(loop != selected) {
      var alias = holder[loop].childNodes;
      alias[0].setAttribute("class","pollViewFormOptionNotSelected");
      alias[1].setAttribute("class","pollViewFormOptionText");
    }
  }

  if (typeof a === "undefined")
    return;

  //Get Parent
  var parentHolder;
  var className = a.getAttribute("class");

  if(className == "pollViewFormOptionA" || className == "pollViewFormOptionB") {
    parentHolder = a;
  }
  else if(className == "pollViewFormOptionText") {
    parentHolder = a.parentNode;
  }
  else if(className == "pollViewFormOptionNotSelected") {
    parentHolder = a.parentNode;
  }
  else if(className == "pollViewFormOptionSelected" || className == "pollViewFormOptionTextSelected" || className == "pollViewFormOptionSelectedCircle") {
    return;
  }

  try {
    var parentHolderChildren = parentHolder.childNodes;
    parentHolder.childNodes[0].setAttribute("class","pollViewFormOptionNotSelectedHover");
    parentHolder.childNodes[1].setAttribute("class","pollViewFormOptionTextHover");
  }
  catch(a) {
  }
}

function castVote(voteIndex) {
  socket.emit('vote', {"option" : voteIndex} );
  if(voteIndex == selected) { //Clicked on the same one
    return;
  }
  var holder = document.getElementById("pollViewFormOptionsAll").childNodes;

  if(selected != -1) { //Clicked on a different one, reset old one; restore to original based on odd or even
    if(selected%2 == 0) {
      holder[selected].setAttribute("class","pollViewFormOptionA");
    }
    else {
      holder[selected].setAttribute("class","pollViewFormOptionB");
    }
    holder[selected].childNodes[0].setAttribute("class","pollViewFormOptionNotSelected");
    holder[selected].childNodes[1].setAttribute("class","pollViewFormOptionText");

  }

  selected = voteIndex;

  for(var loop = 0; loop < viewPollNum; loop++) {
    if(loop != selected) {
      holder[loop].childNodes[0].setAttribute("class","pollViewFormOptionNotSelected");
    }
  }

  holder[voteIndex].setAttribute("class","pollViewFormOptionSelected");
  holder[voteIndex].childNodes[0].setAttribute("class","pollViewFormOptionSelectedCircle");
  holder[voteIndex].childNodes[1].setAttribute("class","pollViewFormOptionTextSelected");

  voteMessage = "You have voted, change your vote by selecting a different option. Poll closes in ";

}

function updatePollTimer() {
  pollTimeLeft--;
  if(pollTimeLeft < 1) {
    //close poll
    clearTimeout(SYSTEM.updatePollTimer);

    document.getElementById("transcript").style.width =  pollObj.toWidth + "px";
    document.getElementById("userlistFrame").style.right = "180px";

    document.getElementById("optionsFrame").style.top = pollObj.top + "px";
    document.getElementById("userlistFrame").style.top = pollObj.top + "px";

    document.getElementById("pollHolder").style.opacity = 1;

    pollObj.originalWidth = parseFloat(document.getElementById("transcript").style.width);
    pollObj.toWidth = pollObj.originalWidth + 200;

    var transcriptH = parseInt(transcript.style.height)/2;
    document.getElementById("userlistFrame").style.height = transcriptH -50 + "px";
    document.getElementById("optionsFrame").style.height = transcriptH + 45+ "px";

    pollObj.top =  transcriptH + 45 - 15; //Used for optionsFrame

    revertToOriginalView(0);

  }
  else {
    var minutes = parseInt(pollTimeLeft/60);
    var seconds;
    if(minutes != 0) {
      seconds = pollTimeLeft - minutes*60;
    }
    else {
      seconds = pollTimeLeft;
    }

    if(seconds < 10) {
      document.getElementById("pollViewFormOptionsLip").innerHTML = voteMessage + minutes + ":0" + seconds;
    }
    else {
      document.getElementById("pollViewFormOptionsLip").innerHTML = voteMessage + minutes + ":" + seconds;
    }

    var rep = "updatePollTimer()";
    SYSTEM.updatePollTimer = setTimeout(rep,1000);
  }
}


/*VISUAL TRANSITIONS---------------------------------------------------------------------------------*/
function animateIntoVoteView(counter) {
  if(counter == 75) {
    clearTimeout(SYSTEM.shrinkTranscript);
    document.getElementById("transcript").style.width =  pollObj.toWidth + "px";
    document.getElementById("userlistFrame").style.right = "180px";

    document.getElementById("optionsFrame").style.top = pollObj.top + "px";
    document.getElementById("userlistFrame").style.top = pollObj.top + "px";

    document.getElementById("pollHolder").style.opacity = 1;

    var rep = "updatePollTimer()";
    SYSTEM.updatePollTimer = setTimeout(rep,1000);

  }
  else {
    counter++;

    document.getElementById("pollHolder").style.opacity = (counter*1.3)/100;

    //Shrink transcript
    var transcriptW = parseFloat(document.getElementById("transcript").style.width);
    var newW = transcriptW - ((transcriptW - pollObj.toWidth)/10);
    document.getElementById("transcript").style.width = newW + "px";

    //Shrink message input
    document.getElementById("message").style.width = (newW + 10) + "px";

    //Reposition userframe div
    //Right:
    var userFrameR = parseFloat(document.getElementById("userlistFrame").style.right);
    var newR = userFrameR + (180 - userFrameR)/10;
    document.getElementById("userlistFrame").style.right = newR + "px";
    //Top:
    var userFrameT = parseFloat(document.getElementById("userlistFrame").style.top);
    var topTo = parseFloat(pollObj.top);
    var newT = userFrameT + (topTo - userFrameT)/10;
    document.getElementById("userlistFrame").style.top = newT + "px";

    var optionsFrameT = parseFloat(document.getElementById("optionsFrame").style.top);
    newT = optionsFrameT + (topTo - optionsFrameT)/10;
    document.getElementById("optionsFrame").style.top = newT + "px";

    voteMessage = "Select an option to vote. Poll closes in "

    var rep = "animateIntoVoteView('"+counter+"')";
    SYSTEM.animateIntoVoteView = setTimeout(rep,10);
  }
}


function revertToOriginalView(counter) {
  if(counter == 75) {
    clearTimeout(SYSTEM.revertToOriginalView);

    document.getElementById("pollHolder").style.opacity = 0;

    document.getElementById("transcript").style.width = pollObj.toWidth + "px";
    document.getElementById("message").style.width = (pollObj.toWidth + 10) + "px";

    document.getElementById("userlistFrame").style.right = "0px";
    document.getElementById("userlistFrame").style.top = "70px";

    document.getElementById("optionsFrame").style.top = pollObj.top + "px";

    //remove pollHolder
    document.body.removeChild(document.getElementById("pollHolder"));
  }
  else {
    counter++;

    document.getElementById("pollHolder").style.opacity = ((75-counter)*1.3)/100;

    //Grow transcript (small to Big)
    var transcriptW = parseFloat(document.getElementById("transcript").style.width);
    var newW = transcriptW + (pollObj.toWidth - transcriptW)/10;
    document.getElementById("transcript").style.width = newW + "px";

    //Grow message input (small to Big)
    document.getElementById("message").style.width = (newW + 10) + "px";

    //Reposition userframe div
      //Right: (Big to small)
      var userFrameR = parseFloat(document.getElementById("userlistFrame").style.right);
      var newR = userFrameR - ((userFrameR - 0)/10);
      document.getElementById("userlistFrame").style.right = newR + "px";
      //Top: (Big to small)
      var userFrameT = parseFloat(document.getElementById("userlistFrame").style.top);
      var newT = userFrameT - (userFrameT - 70)/10;
      document.getElementById("userlistFrame").style.top = newT + "px";

    //Reposition optionsFrame div
      //Top: (Big to small)
      var optionsFrameT = parseFloat(document.getElementById("optionsFrame").style.top);
      newT = optionsFrameT - (optionsFrameT - pollObj.top)/10;
      document.getElementById("optionsFrame").style.top = newT + "px";

    var rep = "revertToOriginalView('"+counter+"')";
    SYSTEM.revertToOriginalView = setTimeout(rep,10);
  }

}
