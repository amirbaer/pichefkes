let name = "tiles-5-basic-4-25";
let version = "0";

function setup() {
	createCanvas(400, 400);
	colorMode(HSB);
}

let v = 0;
function draw() {
	background(220);
	ds4(v);
	v += 10;

	if (v > 360) {
		noLoop();
	}
}

function ds1(v) {
	version = `1-${v}`;
	let ss = 25;

	for (let x = ss; x < width - ss; x += ss) {
		for (let y = ss; y < height - ss; y += ss) {
			for (let i = 0; i < ss; i++) {
				for (let j = 0; j < ss; j++) {
					stroke(i + sin(x)*x + v, j + cos(y)*100, (x+y) % 100);
					point(i + x, j + y);
				}
			}
		}
	}
}

function ds2(v) {
	version = `50-${v}`;
	let ss = 50;

	for (let x = ss; x < width - ss; x += ss) {
		for (let y = ss; y < height - ss; y += ss) {
			for (let i = 0; i < ss; i++) {
				for (let j = 0; j < ss; j++) {
					stroke(i + sin(x)*x + v, j + cos(y)*100, (x+y) % 100);
					point(i + x, j + y);
				}
			}
		}
	}
}

function ds3(v) {
	version = `50-3-${v}`;
	let ss = 50;

	for (let x = ss; x < width - ss; x += ss) {
		for (let y = ss; y < height - ss; y += ss) {
			for (let i = 0; i < ss; i++) {
				for (let j = 0; j < ss; j++) {
					stroke(i + sin(x)*x + v, j + cos(y)*100, 100);
					point(i + x, j + y);
				}
			}
		}
	}
}

function ds4(v) {
	version = `50-4-${v}`;
	let ss = 50 + random(-20, 20);
	v += random(-50, 50)

	for (let x = ss; x < width - ss; x += ss) {
		for (let y = ss; y < height - ss; y += ss) {
			for (let i = 0; i < ss; i++) {
				for (let j = 0; j < ss; j++) {
					stroke(i + sin(x)*x + v, j + cos(y)*100, 100);
					point(i + x, j + y);
				}
			}
		}
	}
}
