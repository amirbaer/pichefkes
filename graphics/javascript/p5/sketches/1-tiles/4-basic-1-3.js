let name = "tiles-4-basic-1-3";
let version = "0";

function setup() {
  createCanvas(400, 400);
  colorMode(HSB);
}

function draw() {
  background(220);
  ds8();
  noLoop();
}

function ds0() {
  version = "0";
  let ss = 10;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds1() {
  version = "1";
  let ss = 1;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds2() {
  version = "2";
  let ss = 2;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds3() {
  version = "3";
  let ss = 3;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds4() {
  version = "4";
  let ss = 4;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds5() {
  version = "5";
  let ss = 5;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds6() {
  version = "20";
  let ss = 20;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds7() {
  version = "25";
  let ss = 25;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds8() {
  version = "50";
  let ss = 50;

  for (let x = ss; x < width - ss; x += ss) {
    for (let y = ss; y < height - ss; y += ss) {
      for (let i = 0; i < ss; i++) {
        for (let j = 0; j < ss; j++) {
          stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
          point(i + x, j + y);
        }
      }
    }
  }
}

function ds10() {
  version = "range-10-200";
  for (let ss = 10; ss < 200; ss += 1) {
      for (let x = ss; x < width - ss; x += ss) {
        for (let y = ss; y < height - ss; y += ss) {
          for (let i = 0; i < ss; i++) {
            for (let j = 0; j < ss; j++) {
              stroke(i + sin(x)*x, j + cos(y)*100, (x+y) % 100);
              point(i + x, j + y);
            }
          }
        }
    }
  }
}
