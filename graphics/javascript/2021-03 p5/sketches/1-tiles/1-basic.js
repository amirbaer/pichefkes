let name = "tiles-basic";
let version = "0";

function setup() {
  createCanvas(400, 400);
  colorMode(HSB);
}

function draw() {
  background(220);
  let ss = 10;
  for (let i = ss; i < width - ss; i += ss) {
    for (let j = ss; j < height - ss; j += ss) {
      draw_square(i, j, ss);
    }
  }

  noLoop();
}

function ds1(x, y, s) {
  version = "1";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(i + sin(x)*x, j + cos(y)*y, x+y);
      point(i + x, j + y);
    }
  }
}

function ds2(x, y, s) {
  version = "2";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(i + sin(x)*x, j + cos(y)*y, (x+y) % 100);
      point(i + x, j + y);
    }
  }
}

function ds3(x, y, s) {
  version = "3";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
      point(i + x, j + y);
    }
  }
}

function ds4(x, y, s) {
  version = "4";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + sin(i)*i, y + sin(j)*j, x+y);
      point(i + x, j + y);
    }
  }
}

function ds5(x, y, s) {
  version = "5";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + sin(i)*i, y + sin(j)*j, (x+y)%100);
      point(i + x, j + y);
    }
  }
}

function ds6(x, y, s) {
  version = "6";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + sin(i)*i, y + sin(j)*j, sin(x+y)*(x+y));
      point(i + x, j + y);
    }
  }
}

function ds7(x, y, s) {
  version = "7";
  s = s / 2;
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + sin(i)*i, y + sin(j)*j, sin(x+y)*(x+y));
      point(i + x, j + y);
    }
  }
}

function ds8(x, y, s) {
  version = "8";
  s = s / 2;
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(y + sin(j)*j, x + sin(i)*i, sin(x+y)*(x+y));
      point(i + x, j + y);
    }
  }
}

function draw_square(x, y, s) {
    ds8(x, y, s);
}

