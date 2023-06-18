#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

void processVideo(const string& inputVideoPath, const string& outputVideoPrefix, double threshold) {
    // Load the video
    VideoCapture video(inputVideoPath);
    if (!video.isOpened()) {
        cout << "Failed to open video file: " << inputVideoPath << endl;
        return;
    }

    // Video properties
    double fps = video.get(CAP_PROP_FPS);
    int width = video.get(CAP_PROP_FRAME_WIDTH);
    int height = video.get(CAP_PROP_FRAME_HEIGHT);
    int totalFrames = video.get(CAP_PROP_FRAME_COUNT);

    // Progress indication variables
    int processedFrames = 0;
    int progressPercentage = 0;
    int prevProgressPercentage = -1;

    // Create a list to store non-black segments
    vector<Rect> segments;

    // Process video frames
    Mat frame;
    int segmentCount = 1;
    bool isSegment = false;
    while (video.read(frame)) {
        // Convert frame to grayscale
        Mat grayscaleFrame;
        cvtColor(frame, grayscaleFrame, COLOR_BGR2GRAY);

        // Calculate average pixel value
        Scalar averagePixelValue = mean(grayscaleFrame);

        // Check if the frame is predominantly black
        if (averagePixelValue[0] <= threshold) {
            if (isSegment) {
                // Continue the existing segment
                segments.back().width++;
            } else {
                // Start a new segment
                segments.emplace_back(frame.cols, frame.rows, processedFrames, segmentCount);
                isSegment = true;
            }
        } else {
            // End the current segment
            isSegment = false;
        }

        // Update progress indication
        processedFrames++;
        progressPercentage = (int)((processedFrames / (double)totalFrames) * 100);
        if (progressPercentage != prevProgressPercentage) {
            cout << "Progress: " << progressPercentage << "%" << endl;
            prevProgressPercentage = progressPercentage;
        }
    }

    // Release video capture
    video.release();

    // Export each non-black segment as a separate video
    for (const Rect& segment : segments) {
        // Set start and end frames for the segment
        int startFrame = segment.x;
        int endFrame = segment.x + segment.width;

        // Reset video capture to the beginning
        video.open(inputVideoPath);

        // Skip frames until the start frame of the segment
        for (int frameIndex = 0; frameIndex < startFrame; ++frameIndex) {
            video.read(frame);
        }

        // Create output video writer
        stringstream ss;
        ss << outputVideoPrefix << "_segment" << segment.y << ".mp4";
        string outputVideoPath = ss.str();
        VideoWriter outputVideo(outputVideoPath, VideoWriter::fourcc('X', '2', '6', '4'), fps, Size(width, height), true);
        if (!outputVideo.isOpened()) {
            cout << "Failed to create output video file: " << outputVideoPath << endl;
            continue;
        }

        // Process frames and write to the output video
        for (int frameIndex = startFrame; frameIndex < endFrame; ++frameIndex) {
            video.read(frame);
            outputVideo.write(frame);
        }

        // Release the output video writer
        outputVideo.release();

        cout << "Segment " << segmentCount << " exported to: " << outputVideoPath << endl;

        segmentCount++;
    }

    cout << "Video processing complete." << endl;
}

int main(int argc, char** argv) {
    // Check if the correct number of command-line arguments are provided
    if (argc != 4) {
        cout << "Usage: " << argv[0] << " <input_video_path> <output_video_prefix> <threshold>" << endl;
        return -1;
    }

    // Parse command-line arguments
    string inputVideoPath = argv[1];
    string outputVideoPrefix = argv[2];
    double threshold = stod(argv[3]);

    // Process the video
    processVideo(inputVideoPath, outputVideoPrefix, threshold);

    return 0;
}
