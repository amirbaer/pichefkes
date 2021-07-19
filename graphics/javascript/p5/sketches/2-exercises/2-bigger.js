let name = "exercises-2-bigger";
let version = "0";

function setup() {
	createCanvas(600, 600);
	colorMode(HSB);
    background(0);
}

function draw() {
	mess4();
    noLoop();
}

function mess() {
    version = "1-mess";

    for (let j = 0; j < 100; j++) {
        for (let i = 0; i < 400; i++) {
            let r = random(400);
            let r2 = random(200);
            stroke((r*pow(-1,j%2)+r2*6)%360, r/200*100+r2/40*20, r2/20*80+20);
            line(width/2+(r-200), height/2+(r-200), r, i);
        }
    }
}

function mess2() {
    version = "2-mess";

    for (let j = 0; j < 100; j++) {
        for (let i = 0; i < 600; i++) {
            let r = random(600);
            let r2 = random(200);
            stroke((r*pow(-1,j%2)+r2*6)%360, r/200*100+r2/40*20, r2/20*80+20);
            line(width/2+(r-200), height/2+(r-200), r+r2, i-r2);
        }
    }
}

function mess3() {
    version = "3-mess";

    for (let j = 0; j < 100; j++) {
        for (let i = 0; i < 600; i++) {
            let r = random(600);
            let r2 = random(200);
            stroke((r*pow(-1,j%2)+r2*6)%50+180, r/200*100+r2/40*20, r2/20*80+20);
            line(width/2+(r/2), height/2+(r/2), r+r2, r-r2);
            line(width*r2/220, height*(550-r)/550, (r2*r)%width, (r2*r)%height);
        }
    }
}

function mess4() {
    version = "4-mess";

    for (let j = 0; j < 100; j++) {
        for (let i = 0; i < 600; i++) {
            let r = random(600);
            let r2 = random(200);
            stroke((r*pow(-1,j%2)+r2*6)%50+180, r/200*100+r2/40*20, r2/20*80+20);
            line(100 + 500*sin(TWO_PI*i/width), 100 + 500*cos(TWO_PI*i/height), r*sin(r2), r2*cos(r));
            //line(width*r2/220, height*(550-r)/550, (r2*r)%width, (r2*r)%height);
        }
    }
}
