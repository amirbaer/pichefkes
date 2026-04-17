/*form methods*/
function create() { //Called when clicking the "create" button
  // Check if form has valid input
  //  [if it doesnt, the errors will be shown to user by form_ok() ]
  if(form_ok()) {
    //create room logic
    var ct_nickname = sjcl.encrypt(window.password, global_user_name);
    socket.emit('create_room',
      {"room":global_room_name, "secret":pass_room_hash, "nick":ct_nickname});
    // reply will come in a socket.on waiting for server's reply
  }
}

// Called when you try to join a room that does not exist
function auto_create(room) { 
  // Check if form has valid input
  //  [if it doesnt, the errors will be shown to user by form_ok() ]
  if(new_form_ok(room)) {

    global_auto_create = true;

    //create room logic
    var ct_nickname = sjcl.encrypt(window.password, global_user_name);
    socket.emit('create_room',
      {"room":global_room_name, "secret":pass_room_hash, "nick":ct_nickname});
    // reply will come in a socket.on waiting for server's reply
  }
}

function join() { //Callend when clicking the join room button
  if(form_ok()) {
    //join room logic
    var ct_nickname = sjcl.encrypt(window.password, global_user_name);
    socket.emit('join_room',
      {"room":global_room_name, "secret":pass_room_hash, "nick":ct_nickname});
  }
}

function new_join(room) { //Callend when clicking the join room button
  if(new_form_ok(room)) {
    //join room logic
    var ct_nickname = sjcl.encrypt(window.password, global_user_name);
    socket.emit('join_room',
      {"room":global_room_name, "secret":pass_room_hash, "nick":ct_nickname});
  }
}

function join_ima() { //Callend when clicking the join room button
  new_join("eilatchatima");
}

function join_bro() { //Callend when clicking the join room button
  new_join("eilatchatbro");
}

function join_boyfriend() { //Callend when clicking the join room button
  new_join("eilatchatboyfriend");
}

function new_form_ok(room) { // Fills global vars, returns true or false based on if form is filled correctly

  // Check if socket failed to open
  if(!socket.socket.open)
    alert("Unable to connect to ChatStep server on port <https>, sorry.");

  //Check if Room name and Nick name are filled
  var nickVal = "";
  if (room == "eilatchatima") {
    nickVal = "annie";
    nickVal = "mother";
    nickVal = "אמא";
  } else if (room == "eilatchatbro") {
    nickVal = "amir";
    nickVal = "sibling";
    nickVal = "אח";
  } else if (room == "eilatchatboyfriend") {
    nickVal = "dmitry";
    nickVal = "partner";
    nickVal = "בן זוג";
  }

  global_user_name = message = nickVal;
  var roomVal = (room).replace(/^#*/, '');
  global_room_name = roomVal;

  // Get base64 sha256 hash of room name
  global_room_hash = sjcl.codec.base64.fromBits(
                    sjcl.hash.sha256.hash(roomVal));

  window.password = global_room_hash +
                    "default_password";


  // base64 hash of password salted with room hash
  pass_room_hash = sjcl.codec.base64.fromBits(
                    sjcl.hash.sha256.hash(window.password + global_room_hash));

  var clientError = "";

  //Check if form filled or not
  var error = false;
  if(nickVal == "" && roomVal == "") {
    clientError = "Enter a nickname and a room";
    error = true;
  } else if(nickVal == "") {
    clientError = "Enter a nickname";
    error = true;
  } else if(roomVal == "") {
    clientError = "Enter a room";
    error = true;
  } else if(nickVal.length > 16) {
    clientError = "Nickname is too long";
    error = true;
  }

  if(error) {
    document.getElementById("modalError").innerHTML = clientError;
    button_enable();
  } else {
    button_disable();
  }

  return (!error);
}

function form_ok() { // Fills global vars, returns true or false based on if form is filled correctly

  // Check if socket failed to open
  if(!socket.socket.open)
    alert("Unable to connect to ChatStep server on port <https>, sorry.");

  // Reset shadows around text boxes
  document.getElementById("nickname").style.boxShadow = "0px 0px 3px lightBlue";
  document.getElementById("room").style.boxShadow = "0px 0px 3px lightBlue";

  //Check if Room name and Nick name are filled
  var nickVal = document.getElementById("nickname").value;
  global_user_name = message = nickVal;
  var roomVal = (document.getElementById("room").value).replace(/^#*/, '');
  global_room_name = roomVal;

  // Get base64 sha256 hash of room name
  global_room_hash = sjcl.codec.base64.fromBits(
                    sjcl.hash.sha256.hash(roomVal));

  window.password = global_room_hash +
                    document.getElementById("password").value +
                    "default_password";


  // base64 hash of password salted with room hash
  pass_room_hash = sjcl.codec.base64.fromBits(
                    sjcl.hash.sha256.hash(window.password + global_room_hash));

  var clientError = "";

  //Check if form filled or not
  var error = false;
  if(nickVal == "" && roomVal == "") {
    clientError = "Enter a nickname and a room";
    document.getElementById("nickname").style.boxShadow = "0px 0px 5px orange";
    document.getElementById("room").style.boxShadow = "0px 0px 5px orange";
    error = true;
  } else if(nickVal == "") {
    clientError = "Enter a nickname";
    document.getElementById("nickname").style.boxShadow = "0px 0px 5px orange";
    document.getElementById("nickname").focus()
    error = true;
  } else if(roomVal == "") {
    clientError = "Enter a room";
    document.getElementById("room").style.boxShadow = "0px 0px 5px orange";
    document.getElementById("room").focus()
    error = true;
  } else if(nickVal.length > 16) {
    clientError = "Nickname is too long";
    document.getElementById("nickname").style.boxShadow = "0px 0px 5px orange";
    document.getElementById("nickname").focus()
    error = true;
  }

  if(error) {
    document.getElementById("modalError").innerHTML = clientError;
    button_enable();
  } else {
    button_disable();
  }

  return (!error);
}

function close_form() {
  document.getElementById('mainTitle').style.height = "55px";
  document.getElementById('chatStepFont').style.font = '32px "Lucida Grande", Helvetica, Arial, sans-serif';
  document.getElementById('mainTitleDesc').style.font = '14px "Lucida Grande", Helvetica, Arial, sans-serif';
  for (i = 0 ; i < 20 ; i++) {
    try {
      document.getElementById('mainTitleBar'+i).style.top = 40;
    } catch(err) {} // this is bad and should be fixed later
  }
  
  document.getElementById('mainTitleDesc').style.opacity = 0;
  var element = document.getElementById("back");
  element.parentNode.removeChild(element);

  document.getElementById('mainTitle').style.background = "none";
  document.getElementById('mainTitle').style.boxShadow = "none";
  //document.body.style.background = "none";
  document.body.style.background = "linear-gradient(to bottom, #ffffff 0%,#f6f6f6 47%,#ededed 100%);";
  document.getElementById('emails').style.zIndex = -1;
  document.getElementById('emails').style.opacity = 0;
  document.getElementById('authors').style.zIndex = -1;
  document.getElementById('authors').style.opacity = 0;
  //document.getElementById('mainTitle').style.opacity = 0;
  //document.styleSheets[0].cssRules[1].style["opacity"] = 0;
  //document.getElementById('mainTitle2').style.opacity = 0.99;
  document.getElementById('mainBox').style.opacity = 0;
  try { // this is bad :(
    //document.getElementById('prompt').style.opacity = 0;
  } catch(err) {
    document.getElementById('promptMobile').style.opacity = 0;
  }
  document.getElementById('transcript').style.height = "615px";

  if(BROWSERINFO.type == "safari") {
    document.getElementById("message").style.opacity = 1;
    document.getElementById("userlistFrame").style.opacity = 1;
    //fade("optionsFrame",0, 20);
  }
  else {
    fade("message",0, 20);
    fade("userlistFrame",0, 20);
    //fade("optionsFrame",0, 20);
  }

  resizeDelay();

  document.getElementById("transcript").style.zIndex = 2;
  document.getElementById("transcript").style.opacity = 1;
    if(global_room_name.length > 15) {
    document.getElementById("userlistTitle").innerHTML = global_room_name;
  }
  else {
    document.getElementById("userlistTitle").innerHTML = "Room: " + global_room_name;
  }
 
  document.getElementById("message").focus();

  //window.location.hash = htmlDecode(global_room_name);
}

/*END FORM METHODS*/

/*FORM SUPPORT METHODS*/
function button_disable() {
  document.getElementById("joinButton").setAttribute("disabled","disabled");
  //document.getElementById("createButton").setAttribute("disabled","disabled");
}

function button_enable() {
  document.getElementById("joinButton").removeAttribute("disabled");
  //document.getElementById("createButton").removeAttribute("disabled");
}
/*END FORM SUPPORT METHODS*/

