let name = "tiles-basic-2-28";
let version = "0";

let v1 = 1;

// CCapture instructions: https://medium.com/@ffmaer/record-p5-js-with-ccapture-js-8e3ac9488ac3

let capturer;
let btn;

function record() {
	capturer = new CCapture({
		format: "png",
		framerate: 24
	});
	capturer.start();
	btn.textContent = "stop recording";
	btn.onclick = e => {
		capturer.stop();
		capturer.save();
		capturer = null;
		btn.textContent = "start recording";
		btn.onclick = record;
	};
}

function setup() {
	createCanvas(400, 400);
	colorMode(HSB);

	// ccapture
	frameRate(24)
	btn = document.createElement("button");
	btn.textContent = "start recording";
	document.body.appendChild(btn);
	btn.onclick = record;
	//btn.click(); //start recording automatically
}

function draw() {
	background(220);
	let ss = 10;
	for (let i = ss; i < width - ss; i += ss) {
		for (let j = ss; j < height - ss; j += ss) {
			draw_square(i, j, ss);
		}
	}

	if (v1 > 500000) {
		noLoop();
	} else {
		//save(`${name}-${version}-${v1}.png`);
	}

	// ccapture
	if (capturer) {
		capturer.capture(document.getElementById("defaultCanvas0"));
	}
}

function ds1(x, y, s) {
	version = "1";

	s = (x * y * s / v1) % 10;
	if (s < 3) {
		s = 3;
	}
	v1 += 1;

	for (let i = 0; i < s; i++) {
		for (let j = 0; j < s; j++) {
			stroke(x + cos(i)*i, y + cos(j)*j, 85+cos(TWO_PI*y/height)*30);
			point(i + x, j + y);
		}
	}
}

function draw_square(x, y, s) {
	ds1(x, y, s);
}

