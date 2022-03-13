var name = "sample";
var version = "1";

function setup() {
    createCanvas(windowWidth, windowHeight);
    background(0);
}

function draw() {
    background(0);
    translate(width/2, height/2);
    rect(0, 0, 100, 100);
    rotate(frameCount/5%TWO_PI)
    circle(20, 0, 40);
}

