let name = "exercises-1-circle";
let version = "0";

function setup() {
	createCanvas(400, 400);
	colorMode(HSB);
    background(0);
}

function draw() {
	play_with_colors();
    noLoop();
}

function basic_circle() {
    version = "1-basic-circle";
    fill(200);
    ellipse(width/2, height/2, 200, 200);
}

function circle_random() {
    version = "2-circle-random-50";
    fill(200);
    ellipse(width/2, height/2, 200, 200);

    for (let i = 0; i < 400; i++) {
        let r = random(50);
        stroke(r * 5);
        line(width/2, height/2, 50 + r, i);
    }
}

function circle_random_full() {
    version = "3-circle-random-400";
    fill(200);
    ellipse(width/2, height/2, 200, 200);

    for (let i = 0; i < 400; i++) {
        let r = random(400);
        stroke(r, r/400*100, 100);
        line(width/2, height/2, 50 + r, i);
    }
}

function circle_random_full_evolving() {
    version = "4-circle-random-full-evolving";

    for (let i = 0; i < 400; i++) {
        let r = random(400);
        let r2 = random(20);
        stroke(r, r*r2/400*100, 100);
        line(width/2, height/2, r, i);
    }

    fill(200);
    stroke(360);
    ellipse(width/2, height/2, 100, 100);
}

function many_circles() {
    version = "5-many-circles";

    for (let i = 0; i < 400; i++) {
        let r = random(400);
        let r2 = random(20);
        stroke(r, r*r2/400*100, 100);
        line(width/2, height/2, r, i);
    }

    let n = 100;
    for (let i = 0; i < n; i++) {

        let r = random(400);
        let r2 = random(20);
        let r3 = random(-5, 5);

        stroke(r, r*r2/400*100, 100);
        fill(r, (r2/20*50)-20, (r/400*20)+20);
        ellipse(width/2, height/2, (100/n)*(n-i)+r3, (100/n)*(n-i)+r3);

    }
}

function more_lines() {
    version = "6-more-lines";

    for (let j = 0; j < 200; j++) {
        for (let i = 0; i < 400; i++) {
            let r = random(400);
            let r2 = random(20);
            stroke(r, r*r2/400*100, 100);
            line(width/2, height/2, r, i);
        }
    }

    let n = 100;
    for (let i = 0; i < n; i++) {

        let r = random(400);
        let r2 = random(20);
        let r3 = random(-5, 5);

        stroke(r, r*r2/400*100, 100);
        fill(r, (r2/20*50)-20, (r/400*20)+20);
        ellipse(width/2, height/2, (100/n)*(n-i)+r3, (100/n)*(n-i)+r3);

    }
}

function play_with_colors() {
    version = "7-play-with-colors";

    for (let j = 0; j < 100; j++) {
        for (let i = 0; i < 400; i++) {
            let r = random(400);
            let r2 = random(20);
            stroke((r*pow(-1,j%2)+r2*16)%360, r/200*100+r2/40*20, r2/20*80+20);
            line(width/2, height/2, r, i);
        }
    }
}

function play_with_colors_bigger_canvas() {
    version = "7-play-with-colors";

    for (let j = 0; j < 100; j++) {
        for (let i = 0; i < 400; i++) {
            let r = random(400);
            let r2 = random(20);
            stroke((r*pow(-1,j%2)+r2*6)%360, r/200*100+r2/40*20, r2/20*80+20);
            line(width/2+(r-200), height/2+(r-200), r, i);
        }
    }
}
