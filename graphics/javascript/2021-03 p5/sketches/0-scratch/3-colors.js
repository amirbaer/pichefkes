let name = "scratch-colors";
let version = "0";


function setup() {
    createCanvas(400, 400);
}

function draw() {
    background(220);
    noStroke();
    draw_rgb();
    draw_hsb();
}

function draw_hsb() {
    colorMode(HSB, 100)
    draw_square(0, 200, 100);
    colorMode(HSB, 200)
    draw_square(100, 200, 200);
    colorMode(HSB, 400)
    draw_square(200, 200, 400);
}

function draw_rgb() {
    colorMode(RGB, 100);
    draw_square(0,0);
    colorMode(RGB, 200);
    draw_square(100,0);
    colorMode(RGB, 10);
    draw_square(0,100);
    colorMode(RGB, 20);
    draw_square(100,100);
    colorMode(RGB, 50);
    draw_square(200,100);
    colorMode(RGB, 75);
    draw_square(300,100);
}

function draw_square(x, y, v=0) {
    for (let i = 0; i < 100; i++) {
        for (let j = 0; j < 100; j++) {
            stroke(i, j, v);
            point(i + x, j + y);
        }
    }
}

