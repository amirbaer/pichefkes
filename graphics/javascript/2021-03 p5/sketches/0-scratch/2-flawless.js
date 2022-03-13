let name = "scratch-flawless";
let version = "0";

let x = 0;
var c;
var c2;
var r = 1;

function setup() {
  createCanvas(700, 650);
  background(0);
  c = color(0, 0, 0);
  c2 = color(0, 0, 0);
}

function d1() {
  version = "1";
  //background(0);
  //ellipse(mouseX, mouseY, 80, 80);
  
  noStroke();
  
  c.setAlpha(abs(sin(x*100))*255);
  //c.setAlpha((alpha(c)+1)%255);
  c.setRed((red(c) + 1) % 200);
  c.setGreen((green(c) + 2) % 60);
  c.setBlue((blue(c) + 2) % 160);
  
  c2.setAlpha(abs(sin(x*100))*255);
  //c.setAlpha((alpha(c)+1)%255);
  c2.setRed((red(c2) + 1) % 255 + 20);
  c2.setGreen((green(c2) + 2) % 160);
  c2.setBlue((blue(c2) + 2) % 60);
  
  fill(c);
  ellipse(x + sin(x) * 10, height/2 + sin(x/2) * 50, 5, 5);
  //ellipse(x + sin(x) * 10, height/2 + sin(x/2) * 100, 5, 5);
  fill(c2);
  ellipse(x + sin(x) * 10, height/2 + sin(x/2) * 200, 5, 5);
  
  fill(color("white"));
  ellipse(x, height/2, abs(sin(x/10))*10, abs(sin(x/10))*10);
  r = (r + 0.25) % 40;
  
  x = x + 1;
  if(x > width + 45) {
    x = -45;
    noLoop();
  }
}

function d2() {
  version = "2";
  
  noStroke();
  
  c.setAlpha(abs(sin(x*100))*255);
  c.setAlpha((alpha(c)+1)%255);
  c.setRed((red(c) + 1) % 200);
  c.setGreen((green(c) + 2) % 60);
  c.setBlue((blue(c) + 2) % 160);
  
  c2.setAlpha(abs(sin(x*100))*255);
  c2.setAlpha((alpha(c)+1)%255);
  c2.setRed((red(c2) + 1) % 255 + 20);
  c2.setGreen((green(c2) + 2) % 160);
  c2.setBlue((blue(c2) + 2) % 60);
  
  fill(c);
  ellipse(x + sin(x) * 10, height/2 + sin(x/2) * 50, 5, 5);
  //ellipse(x + sin(x) * 10, height/2 + sin(x/2) * 100, 5, 5);
  fill(c2);
  ellipse(x + sin(x) * 10, height/2 + sin(x/2) * 200, 5, 5);
  
  fill(color("white"));
  ellipse(x, height/2, abs(sin(x/10))*10, abs(sin(x/10))*10);
  r = (r + 0.25) % 40;
  
  x = x + 1;
  if(x > width + 45) {
    x = -45;
    noLoop();
  }
}

function draw() {
	d2();
}
