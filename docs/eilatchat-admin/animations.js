
function fade(id, index, counter) {
  document.getElementById(id).style.opacity = (20 - counter) * 0.05;
  //Reload
  counter--;
  var rep = "fade('"+id+"','"+index+"','"+counter+"')";
    TIME[SYSTEM.id] = setTimeout(rep,5);
    if(counter == 0) {
      clearTimeout(TIME[SYSTEM.id]);
      delete TIME[SYSTEM.id];
      //imageStack[index].done = true;
    }
}

/*SHOW FEATURES HOME SCREEN*/
var featureDetailU = ["-86.00%", "-73.75%", "-63.03%", "-53.65%", "-45.44%", "-38.26%", "-31.98%", "-26.48%", "-21.67%", "-17.46%", "-13.78%", "-10.56%", "-7.74%", "-5.27%", "-3.11%", "-1.22%", "0.43%", "1.88%", "3.15%", "4.26%", "5.23%", "6.08%", "6.82%", "7.47%", "8.04%", "8.54%", "8.97%", "9.35%", "9.68%", "9.97%", "10.22%", "10.44%", "10.63%", "10.80%", "10.95%", "11.08%", "11.20%", "11.30%", "11.39%", "11.47%", "11.54%", "11.60%", "11.65%", "11.69%", "11.73%", "11.76%", "11.79%", "11.82%", "11.84%", "12%"];
var featureU = ["12.50%", "23.44%", "33.01%", "41.38%", "48.71%", "55.12%", "60.73%", "65.64%", "69.94%", "73.70%", "76.99%", "79.87%", "82.39%", "84.59%", "86.52%", "88.20%", "89.67%", "90.96%", "92.09%", "93.08%", "93.94%", "94.70%", "95.36%", "95.94%", "96.45%", "96.89%", "97.28%", "97.62%", "97.92%", "98.18%", "98.41%", "98.61%", "98.78%", "98.93%", "99.06%", "99.18%", "99.28%", "99.37%", "99.45%", "99.52%", "99.58%", "99.63%", "99.68%", "99.72%", "99.75%", "99.78%", "99.81%", "99.83%", "99.85%", "100%"];
var promptR = ["-28.75px", "-62.66px", "-92.33px", "-118.29px", "-141.00px", "-160.88px", "-178.27px", "-193.49px", "-206.80px", "-218.45px", "-228.64px", "-237.56px", "-245.37px", "-252.20px", "-258.18px", "-263.41px", "-267.98px", "-271.98px", "-275.48px", "-278.55px", "-281.23px", "-283.58px", "-285.63px", "-287.43px", "-289.00px", "-290.38px", "-291.58px", "-292.63px", "-293.55px", "-294.36px", "-295.06px", "-295.68px", "-296.22px", "-296.69px", "-297.10px", "-297.46px", "-297.78px", "-298.06px", "-298.30px", "-298.51px", "-298.70px", "-298.86px", "-299.00px", "-299.13px", "-299.24px", "-299.34px", "-299.42px", "-299.49px", "-299.55px", "-299.61px"];

var featureDetailD = ["-2.00%", "-14.25%", "-24.97%", "-34.35%", "-42.56%", "-49.74%", "-56.02%", "-61.52%", "-66.33%", "-70.54%", "-74.22%", "-77.44%", "-80.26%", "-82.73%", "-84.89%", "-86.78%", "-88.43%", "-89.88%", "-91.14%", "-92.25%", "-93.22%", "-94.07%", "-94.81%", "-95.46%", "-96.03%", "-96.53%", "-96.96%", "-97.34%", "-97.67%", "-97.96%", "-98.21%", "-98.43%", "-98.63%", "-98.80%", "-98.95%", "-99.08%", "-99.19%", "-99.29%", "-99.38%", "-99.46%", "-99.53%", "-99.59%", "-99.64%", "-99.69%", "-99.73%", "-99.76%", "-99.79%", "-99.82%", "-99.84%", "-99.86%"];
var featureD = ["89.00%", "79.38%", "70.96%", "63.59%", "57.14%", "51.50%", "46.56%", "42.24%", "38.46%", "35.15%", "32.26%", "29.73%", "27.51%", "25.57%", "23.87%", "22.39%", "21.09%", "19.95%", "18.96%", "18.09%", "17.33%", "16.66%", "16.08%", "15.57%", "15.12%", "14.73%", "14.39%", "14.09%", "13.83%", "13.60%", "13.40%", "13.22%", "13.07%", "12.94%", "12.82%", "12.72%", "12.63%", "12.55%", "12.48%", "12.42%", "12.37%", "12.32%", "12.28%", "12.24%", "12.21%", "12.18%", "12.16%", "12.14%", "12.12%", "12.10%"];
var promptL = ["-258.50px", "-222.19px", "-190.42px", "-162.62px", "-138.29px", "-117.00px", "-98.38px", "-82.08px", "-67.82px", "-55.34px", "-44.42px", "-34.87px", "-26.51px", "-19.20px", "-12.80px", "-7.20px", "-2.30px", "1.99px", "5.74px", "9.02px", "11.89px", "14.40px", "16.60px", "18.53px", "20.21px", "21.68px", "22.97px", "24.10px", "25.09px", "25.95px", "26.71px", "27.37px", "27.95px", "28.46px", "28.90px", "29.29px", "29.63px", "29.93px", "30.19px", "30.42px", "30.62px", "30.79px", "30.94px", "31.07px", "31.19px", "31.29px", "31.38px", "31.46px", "31.53px", "31.59px"];

function initShow() {
  showFeatures(50);
  document.getElementById("allFeatures").setAttribute("onclick","");
}

function initHide() {
  hideFeatures(50);
  document.getElementById("allFeatures").setAttribute("onclick","");
}

function showFeatures(counter) {
  //RELOAD
  if(counter == 0) {
    clearTimeout(SYSTEM.slideTime);
    document.getElementById("allFeatures").innerHTML = "< Go Back";
    document.getElementById("allFeatures").setAttribute("onclick","initHide()");
  }
  else {
    //document.getElementById("prompt").style.right = promptR[50 - counter];
    //document.getElementById("feature").style.bottom = featureU[50 - counter];
    //document.getElementById("featureDetail").style.bottom = featureDetailU[50 - counter];
    counter--;
    var rep = "showFeatures("+counter+")";
    SYSTEM.slideTime = setTimeout(rep,15);
  }
}

function hideFeatures(counter) {
  //RELOAD
  if(counter == 0) {
    clearTimeout(SYSTEM.slideTime);
    document.getElementById("allFeatures").innerHTML = "Read More >";
    document.getElementById("allFeatures").setAttribute("onclick","initShow()");
  }
  else {
    //document.getElementById("prompt").style.right = promptL[50 - counter];
    //document.getElementById("feature").style.bottom = featureD[50 - counter];
    //document.getElementById("featureDetail").style.bottom = featureDetailD[50 - counter];
    counter--;
    var rep = "hideFeatures("+counter+")";
    SYSTEM.slideTime = setTimeout(rep,15);
  }
}
/*END SHOW FEATURES HOME SCREEN*/

/*CORE CHAT VISUALS*/

function onWindowFocus() {
  clearUnread();
  hasFocus = true;
  if(global_user_id != -1) {// actually in a room
    sendActive(true);
    updateUniqueStatusUI(global_user_id, {"active": true});
  }
}

function onWindowBlur() {
  hasFocus = false;
  if(global_user_id != -1)
    sendActive(false);
}

function scrollToBottom() {
  var transcript = document.getElementById("transcript");
  transcript.scrollTop = transcript.scrollHeight;
}

function typingStopped() {
  if(isTyping) {
    isTyping = false;
    sendTyping(false);
    updateUniqueStatusUI(global_user_id, {"active": hasFocus, "typing": isTyping});
  }
}

var timer;
function keyTyped() { // called on keyup event from message input text box
  if(timer) window.clearTimeout(timer); // reset timer when a key is typed
  timer = window.setTimeout(typingStopped, 250);
  if(!isTyping) {
    isTyping = true;
    sendTyping(true);
    updateUniqueStatusUI(global_user_id, {"active": hasFocus, "typing": isTyping});
  }
}

function incrementUnread() {
  if(!hasFocus) {
    unread++;
    document.title = "(" + unread + ") EilatChatAdmin";

    if(soundNotifications) {
      var snd = new Audio("https://chatstep.com/ding.wav");
      snd.volume = 0.2;
      snd.play();
    }
  }
}

function clearUnread() {
  unread = 0;
  document.title = "EilatChatAdmin";
}
/*END CORE CHAT VISUALS*/
