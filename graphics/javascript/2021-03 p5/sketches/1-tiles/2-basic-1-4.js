let name = "tiles-basic4";
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
      stroke(x + sin(i)*i, y + sin(j)*j, x+y);
      point(i + x, j + y);
    }
  }
}

function ds2(x, y, s) {
  version = "2";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, x+y);
      point(i + x, j + y);
    }
  }
}

function ds3(x, y, s) {
  version = "3";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 20+((x+y)%20));
      point(i + x, j + y);
    }
  }
}

function ds4(x, y, s) {
  version = "4";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 40+((x+y)%40));
      point(i + x, j + y);
    }
  }
}

function ds5(x, y, s) {
  version = "5";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 60+((x+y)%60));
      point(i + x, j + y);
    }
  }
}

function ds6(x, y, s) {
  version = "6";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 60+((x+y)%80));
      point(i + x, j + y);
    }
  }
}

function ds7(x, y, s) {
  version = "7";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 60+((x+y)%100));
      point(i + x, j + y);
    }
  }
}

function ds8(x, y, s) {
  version = "8";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 95+(sin(i)*10));
      point(i + x, j + y);
    }
  }
}

function ds9(x, y, s) {
  version = "9";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 95+(sin(i+j)*10));
      point(i + x, j + y);
    }
  }
}

function ds10(x, y, s) {
  version = "10";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 95+(sin(j)*10));
      point(i + x, j + y);
    }
  }
}

function ds11(x, y, s) {
  version = "11";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 95+(sin(x)*10));
      point(i + x, j + y);
    }
  }
}

function ds12(x, y, s) {
  version = "12";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 95+(sin(y)*10));
      point(i + x, j + y);
    }
  }
}

function ds13(x, y, s) {
  version = "13";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 95+(sin(x+y)*10));
      point(i + x, j + y);
    }
  }
}

function ds14(x, y, s) {
  version = "14";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 95+(y/height)*10);
      point(i + x, j + y);
    }
  }
}

function ds15(x, y, s) {
  version = "15";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 80+sin(y/TWO_PI)*20);
      point(i + x, j + y);
    }
  }
}

function ds16(x, y, s) {
  version = "16";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 80+sin(TWO_PI*y*2/height)*20);
      point(i + x, j + y);
    }
  }
}

function ds17(x, y, s) {
  version = "17";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 80+sin(TWO_PI*y/height)*20);
      point(i + x, j + y);
    }
  }
}

function ds18(x, y, s) {
  version = "18";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 80+cos(TWO_PI*y/height)*20);
      point(i + x, j + y);
    }
  }
}

function ds19(x, y, s) {
  version = "19";
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds20(x, y, s) {
  version = "20";
  s = 1;
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds21(x, y, s) {
  version = "21";
  s = (x * y * s) % 10;
  if (s < 3) {
    s = 3;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds22(x, y, s) {
  version = "22";
  s = (x * y * s / 3) % 10;
  if (s < 3) {
    s = 5;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds23(x, y, s) {
  version = "23";
  s = (x * y * s / 3) % 10;
  if (s < 3) {
    s = 3;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds24(x, y, s) {
  version = "24";
  s = (x * y * s / 7) % 10;
  if (s < 3) {
    s = 3;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds25(x, y, s) {
  version = "25";
  s = (x * y * s / 13) % 10;
  if (s < 3) {
    s = 3;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds26(x, y, s) {
  version = "26";
  s = (x * y * s / 713) % 10;
  if (s < 3) {
    s = 3;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds27(x, y, s) {
  version = "27";
  s = (x * y * s / 1713) % 10;
  if (s < 3) {
    s = 3;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function ds28(x, y, s) {
  version = "28";
  s = (x * y * s / 17413) % 10;
  if (s < 3) {
    s = 3;
  }
  for (let i = 0; i < s; i++) {
    for (let j = 0; j < s; j++) {
      stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
      point(i + x, j + y);
    }
  }
}

function draw_square(x, y, s) {
    ds28(x, y, s);
}

