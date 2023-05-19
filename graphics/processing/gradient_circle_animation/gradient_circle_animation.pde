int img_size = 1000;
color start_color1 = color(0, 0, 255);
color start_color2 = color(255, 0, 0);
color end_color = color(255, 255, 255);
float gradient_start = 0.5;
int num_frames = 144;
int circle_radius;
float rotation_angle = 0.0;

void settings() {
  size(img_size, img_size);
}

void setup() {
  circle_radius = (int) (img_size * 0.45);
  colorMode(RGB, 1);
  frameRate(30);  // Adjust the frame rate as desired
}

void draw() {
  float angleOffset = (TWO_PI / num_frames) * frameCount;
  rotation_angle = (rotation_angle + angleOffset) % TWO_PI;
  
  background(255);

  for (int y = 0; y < height; y++) {
    for (int x = 0; x < width; x++) {
      float distance = dist(x, y, width/2, height/2);
      if (distance <= circle_radius) {
        float angle = atan2(y - height/2, x - width/2);
        float adjusted_angle = (angle + rotation_angle) % TWO_PI;
        if (adjusted_angle < 0) adjusted_angle += TWO_PI;
        float gradient = map(adjusted_angle, 0, TWO_PI, 0, 1);
        if (gradient < gradient_start) {
          set(x, y, lerpColor(start_color1, start_color2, gradient / gradient_start));
        } else {
          set(x, y, lerpColor(start_color2, end_color, (gradient - gradient_start) / (1 - gradient_start)));
        }
      }
    }
  }
  
  saveFrame("frame-####.png");
  
  if (frameCount == num_frames) {
    exit();  // Stop the program after generating all frames
  }
  
  frameCount++;
}
