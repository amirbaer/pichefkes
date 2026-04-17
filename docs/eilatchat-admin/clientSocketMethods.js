/*SOCKET RELATED METHODS*/

// Recieve server response about login attempt
// Types: 1 - Room successfully created
//        2 - Room could not be created
//        3 - Room successfully joined
//        4 - Room has diff password
//        5 - Room doesn't exist
//        6 - Created a duplicate room
socket.on('create_or_join_reply', function(reply) {
  if (reply.type == 1) {
    close_form();
    //document.getElementById("transcript").innerHTML += "<div class='rec_message'><span class='other'>" +
    //  " You have successfully created the chat room " + global_room_name + ".</span></div>";
    document.getElementById("transcript").innerHTML += "<div class='rec_message'><span class='other'>" +
      " Welcome </span></div>";
    global_user_id = reply.user_info.unique;

    alert("יש לרענן את העמוד לאחר השימוש");
    
  } else if (reply.type == 3) {
    close_form();
    //document.getElementById("transcript").innerHTML += "<div class='rec_message'><span class='other'>" +
    //  " You have successfully joined the chat room " + global_room_name + ".</span></div>";
    document.getElementById("transcript").innerHTML += "<div class='rec_message'><span class='other'>" +
      " Welcome </span></div>";
    global_user_id = reply.user_info.unique;

    alert("יש לרענן את העמוד לאחר השימוש");
    
  } else if (reply.type == 2 || reply.type == 4) {
    document.getElementById("modalError").innerHTML =
      "The room has been created with a different password.";
    button_enable();
  } else if (reply.type == 5) {
    if (!global_auto_create) {
        auto_create(global_room_name);
    } else {
        document.getElementById("modalError").innerHTML =
          "The room does not exist yet, ask Eilat to create it for you (" + global_room_name + ")";
        button_enable();
    }
  } else if (reply.type == 6) {
    document.getElementById("modalError").innerHTML =
      "The room has been already been created, try joining it?";
    button_enable();
  } else if (reply.type == 7) {
    document.getElementById("modalError").innerHTML =
      "The room has too many users, sorry.";
    button_enable();
  } else {
    socket.disconnect();
    location.reload();
  }

  //Update Bar at top
  var colors = ["lightPink", "lightSalmon", "orange", "lightGreen", "lightBlue"];
  //console.log(document.getElementById("barholder"));
  document.getElementById("barholder").innerHTML = "";

  var winW, winH;
  if (BROWSER.name) {
    winW = window.innerWidth;
    winH = window.innerHeight;
  } else {
    winW = document.documentElement.clientWidth;
    winH = document.documentElement.clientHeight;
  }


  var length = 0;
  for (var a in roomData) {
    length++;
  }

  var lengthOfBar = (winW - 280) / length;
  var loopA = 1;
  for (var a in roomData) {
//    console.log(roomData[a]["color"])
    //colors[roomData[a]["color"]]

    var bottom = document.createElement("div");
    bottom.setAttribute("class", "mainTitleBar2");
    bottom.style.left = 200 + (loopA - 1) * lengthOfBar + "px";
    bottom.style.width = lengthOfBar + "px";
    bottom.style.background = bar[roomData[a]["color"]]
    document.getElementById("barholder").appendChild(bottom);
    loopA++;
  }


});

function cleaner(str) {
	str = str.replace(/<(?:.|\n)*?>/gm, '');
	str = str.replace(/</gm, '&lt;');
	str = str.replace(/>/gm, '&gt;');
	str = str.replace(/"/gm, '&quot;');
	str = str.replace(/'/gm, '&#039;');
	return str;
}

// Action upon recieving a new chat message.
socket.on('new', function(data) {
  try {
    if (document.getElementById("transcript").childNodes.length > 5) {
      document.getElementById("fog").style.opacity = 1;
      transcriptExtra = true;
      resizeDelay();
    }

    var pt_nickname = sjcl.decrypt(window.password, data.nickname);
    var pt_message = sjcl.decrypt(window.password, data.message);
    var unique_id = data.unique;
    // protect against any manipulation from other clients to inject html/js
    pt_nickname = cleaner(pt_nickname);
    pt_message = cleaner(pt_message);
    var result = parseMessage(pt_message)
    var parsed_pt_message = result[0];
    if (result[1].length != 0) {
      handleYoutube(result, false, pt_nickname, unique_id);
    } else {
      createBubble(pt_nickname, unique_id, parsed_message, false);
    }
    scrollToBottom();
    incrementUnread();
  } catch (err) {}
});

// Action upon recieving a new file.
socket.on('new_file', function(data) {
  try {
    var pt_nickname = sjcl.decrypt(window.password, data.nickname);
    var pt_file = sjcl.decrypt(window.password, data.file);
    pt_nickname = cleaner(pt_nickname);
    pt_file = cleaner(pt_file);
    // Set max recieved image width as a percent of window width
    var max_width = 0.75 * window.innerWidth;
    var color = roomData[data.unique]["color"] + "Yt";
    if(showImagesOption) { // show images is opt-out
      document.getElementById("transcript").innerHTML += "<div class='rec_message'><img  class ='" + color +
        "' OnLoad='scrollToBottom();' style='max-width: " + max_width +
        "px;' src='" + pt_file + "' /></div>";
      incrementUnread();
    }
  } catch (err) {
    console.log(err);
  }
});

// Action when the server sends updated encrytped userlist.
socket.on('list', function(data) {
  try {
    document.getElementById("userlist").innerHTML = "";
    for (var i = 0; i <= data.userlist.length; i++) {
      if (data.userlist[i] != undefined) {
        var nickname_ct = data.userlist[i].nickname;
        var nickname_pt = sjcl.decrypt(window.password, nickname_ct);
        var unique_id = data.userlist[i].unique;
        if (roomData[unique_id] == null) {
          roomData[unique_id] = new Object();
        }
        var color = data.userlist[i].color;
        var active = data.userlist[i].active;
        var cur_name = cleaner(nickname_pt);

        roomData[unique_id]["color"] = color;
        roomData[unique_id]["active"] = active;

        var typing = document.createElement("div");
        typing.setAttribute("class", "typing");
        typing.setAttribute("id", "typing" + unique_id);
        typing.style.opacity = 0;

        var firstDot = document.createElement("div");
        firstDot.setAttribute("class", roomData[unique_id]["color"] + "Box");
        firstDot.style.borderRadius = "5px";
        firstDot.style.width = "10px";
        firstDot.style.height = "10px";
        firstDot.style.left = "1px";
        typing.appendChild(firstDot);

        var firstDot = document.createElement("div");
        firstDot.setAttribute("class", roomData[unique_id]["color"] + "Box");
        firstDot.style.borderRadius = "5px";
        firstDot.style.width = "10px";
        firstDot.style.height = "10px";
        firstDot.style.left = "14px";
        typing.appendChild(firstDot);

        var firstDot = document.createElement("div");
        firstDot.setAttribute("class", roomData[unique_id]["color"] + "Box");
        firstDot.style.borderRadius = "5px";
        firstDot.style.width = "10px";
        firstDot.style.height = "10px";
        firstDot.style.left = "26px";
        typing.appendChild(firstDot);



        typing.style.top = i * 24 + "px";
        document.getElementById("userlist").appendChild(typing);

        var box = document.createElement("div");
        box.setAttribute("class", "userlistBox");
        box.setAttribute("id", "box" + unique_id);

        var color = document.createElement("div");
        color.setAttribute("class", roomData[unique_id]["color"] + "Box");

        box.setAttribute("class", roomData[unique_id]["color"] + "Box");

        var name = document.createElement("div");
        name.setAttribute("class", "userlistName");
        name.appendChild(document.createTextNode(htmlDecode(cur_name)));
        //name.style = "background: #C3D9FF;background: -moz-linear-gradient(top, rgba(195, 217, 255, 1) 0%, rgba(177, 200, 239, 1) 41%, rgba(152, 176, 217, 1) 100%);\background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(195, 217, 255, 1)), color-stop(41%,rgba(177, 200, 239, 1)), color-stop(100%,rgba(152, 176, 217, 1)));background: -webkit-linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);background: -o-linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);background: -ms-linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);background: linear-gradient(top, rgba(195, 217, 255, 1) 0%,rgba(177, 200, 239, 1) 41%,rgba(152, 176, 217, 1) 100%);box-shadow: 0px 0px 5px #C3D9FF;"
        //alert(roomData[unique_id]["color"]);

        //box.appendChild(color);
        box.appendChild(name);
        //color.style.top = i*20 + "px";
        box.style.top = i * 24 + "px";

        //get size
        var sizeTest = document.createElement("span");
        sizeTest.setAttribute("class", "nameSpan");
        sizeTest.appendChild(document.createTextNode(htmlDecode(cur_name)));
        document.body.appendChild(sizeTest);
        var temp = sizeTest.clientWidth;

        if (temp > 125) {
          largestUser = 125;
        } else {
          if (largestUser < temp) {
            largestUser = temp;
            //update size
            largeUpdate();
          }
        }
        sizeTest.parentNode.removeChild(sizeTest);
        document.getElementById("userlist").appendChild(box);


        // Update box to be dimmed based on user status
        var status = {
          "active": active
        };
        updateUniqueStatusUI(unique_id, status);
      }
    }
  } catch (err) {
    console.log(err.toString());
  }

  /*
    for(; loopA < max; loopA++) {
    var bottom = document.createElement("div");
    var currentColor = roomData[a]["color"]
    bottom.setAttribute("class","mainTitleBar");
    //bottom.setAttribute("id","mainTitleBar" + loopA);
    bottom.style.boxShadow = "0px 0px 15px 10px " + currentColor;
    bottom.style.left = loopA*200 +"px";
    colors.unshift(currentColor);
    document.getElementById("barholder").appendChild(bottom);
    //document.body.appendChild(bottom);
  }
  */

  //Update Bar at top
  var colors = ["lightPink", "lightSalmon", "orange", "lightGreen", "lightBlue"];
  //console.log(document.getElementById("barholder"));
  document.getElementById("barholder").innerHTML = "";

  var winW, winH;
  if (BROWSER.name) {
    winW = window.innerWidth;
    winH = window.innerHeight;
  } else {
    winW = document.documentElement.clientWidth;
    winH = document.documentElement.clientHeight;
  }


  var length = 0;
  for (var a in roomData) {
    length++;
  }
  //alert("JOINED LENGTH: " + length);

  var lengthOfBar = (winW - 280) / length;
  var loopA = 1;
  for (var a in roomData) {
    var bottom = document.createElement("div");
    bottom.setAttribute("class", "mainTitleBar2");
    bottom.style.left = 200 + (loopA - 1) * lengthOfBar + "px";
    bottom.style.width = lengthOfBar + "px";
    bottom.style.background = bar[roomData[a]["color"]]
    document.getElementById("barholder").appendChild(bottom);
    loopA++;
  }



});

// Action when a new user joins.
socket.on('new_user', function(data) {
  try {
    var pt_nickname = sjcl.decrypt(window.password, data.nickname);
    pt_nickname = cleaner(pt_nickname);
    document.getElementById("transcript").innerHTML += "<div class='rec_message'><span class='other'>" + pt_nickname +
      " joined</span></div>";
    scrollToBottom();
    incrementUnread();
  } catch (err) {
    console.log(err);
  }



});

function updateUniqueStatusUI(unique_id, status) {
  try {
    // Update UI according to new status
    var curBox = document.getElementById("box" + unique_id);
    var typeBox = document.getElementById("typing" + unique_id);
    if (status.active == true) {
      curBox.style.opacity = 1.0;
      if (status.typing == true) {
        // enable UI EVENT FOR user unique_id actively typing
        typeBox.style.opacity = 1;
      } else {
        // enable UI EVENT FOR user unique_id stop typing
        typeBox.style.opacity = 0;
      }
    } else {
      curBox.style.opacity = 0.5;
    }
  } catch (err) {
    console.log(err);
  }
}

// Action when a user updates their status
socket.on('status_broadcast', function(data) {
  try {
    updateUniqueStatusUI(data.unique, data.status);
  } catch (err) {
    console.log(err);
  }
});

// Action when a user leaves.
socket.on('dead_user', function(data) {
  try {
  //  console.log(data);
    var pt_nickname = sjcl.decrypt(window.password, data.nickname);
    pt_nickname = cleaner(pt_nickname);

    document.getElementById("transcript").innerHTML += "<div class='rec_message'><span class='other'>" + pt_nickname +
      " left</span></div>";
    scrollToBottom();
    incrementUnread();
  } catch (err) {
    console.log(err);
  }

  //Update Bar at top
  var colors = ["lightPink", "lightSalmon", "orange", "lightGreen", "lightBlue"];
  //console.log(document.getElementById("barholder"));
  document.getElementById("barholder").innerHTML = "";

  var winW, winH;
  if (BROWSER.name) {
    winW = window.innerWidth;
    winH = window.innerHeight;
  } else {
    winW = document.documentElement.clientWidth;
    winH = document.documentElement.clientHeight;
  }

  delete roomData[data.unique];

  var length = 0;
  for (var a in roomData) {
    length++;
  }

  var lengthOfBar = (winW - 280) / length;
  var loopA = 1;
  for (var a in roomData) {
//    console.log(roomData[a]["color"])
//    colors[roomData[a]["color"]]

    var bottom = document.createElement("div");
    bottom.setAttribute("class", "mainTitleBar2");
    bottom.style.left = 200 + (loopA - 1) * lengthOfBar + "px";
    bottom.style.width = lengthOfBar + "px";
    bottom.style.background = bar[roomData[a]["color"]]
    document.getElementById("barholder").appendChild(bottom);
    loopA++;
  }


});

socket.on('disconnect', function (data) {
	alert("Network Connection Error: Please refresh the page.");
});

socket.on('error', function (data) {
	//alert("Network Connection Error: Please refresh the page.");
});

/*END SOCKET RELATED METHODS*/
