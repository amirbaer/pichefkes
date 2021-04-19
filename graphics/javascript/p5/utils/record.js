// the frame rate
var fps = 60;

// the canvas capturer instance
var capturer = new CCapture({ format: 'png', framerate: fps });

// setup the drawing
function setup() {
  createCanvas(540, 540);

  // this is optional, but lets us see how the animation will look in browser.
  frameRate(fps);
}

// draw
var startMillis; // needed to subtract initial millis before first draw to begin at t=0.
function draw() {
  if (frameCount === 1) {
    // start the recording on the first frame
    // this avoids the code freeze which occurs if capturer.start is called
    // in the setup, since v0.9 of p5.js
    capturer.start();
  }

  if (startMillis == null) {
    startMillis = millis();
  }

  // duration in milliseconds
  var duration = 3000;

  // compute how far we are through the animation as a value between 0 and 1.
  var elapsed = millis() - startMillis;
  var t = map(elapsed, 0, duration, 0, 1);

  // if we have passed t=1 then end the animation.
  if (t > 1) {
    noLoop();
    console.log('finished recording.');
    capturer.stop();
    capturer.save();
    return;
  }

  // actually draw
  blendMode(BLEND);
  background(240);
  blendMode(MULTIPLY);
  translate(width / 2, height / 2);

  var radius = 70;
  var circles = [
    color(250, 50, 0),
    color(50, 250, 0),
    color(0, 50, 250),
    color(250, 250, 0),
    color(250, 0, 250),
    color(0, 250, 250),
  ];

  for (var i = 0; i < circles.length; i++) {
    noStroke();
    fill(circles[i]);

    var tPow = Math.pow(t, map(i, 0, circles.length - 1, 1, 2));
    ellipse(
      (width * 0.4 - radius / 2) * Math.sin(tPow * TAU),
      (height * 0.4 - radius / 2) * Math.cos(tPow * TAU + PI),
      radius
    );
  }
  // end drawing code

  // handle saving the frame
  console.log('capturing frame');
  capturer.capture(document.getElementById('defaultCanvas0'));
}
