#!/usr/bin/env python3.12

import os
import cv2
import subprocess
from datetime import datetime
import numpy as np
import tempfile
from pathlib import Path

class VideoProcessor:
    def __init__(self, input_folder):
        self.input_folder = Path(input_folder)
        self.temp_dir = Path(tempfile.mkdtemp())
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.font_color = (255, 255, 255)  # White
        self.font_thickness = 2
        self.target_size = None  # Will be set based on largest video dimension
        
    def get_creation_date(self, file_path):
        """Get creation date from video metadata or file creation date."""
        try:
            # Try to get creation date from video metadata using ffprobe
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-select_streams', 'v:0',
                '-show_entries', 'stream_tags=creation_time',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(file_path)
            ], capture_output=True, text=True)
            
            if result.stdout.strip():
                # Parse ISO format date from metadata
                return datetime.strptime(result.stdout.strip(), '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            pass
        
        # Fallback to file creation time
        return datetime.fromtimestamp(os.path.getctime(file_path))

    def get_video_info(self, video_path):
        """Get video dimensions and frame rate."""
        cap = cv2.VideoCapture(str(video_path))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return width, height, fps, frame_count
    
    def determine_target_size(self, videos):
        """Determine target size based on largest video dimension."""
        max_dimension = 0
        for video_path, _ in videos:
            width, height, _, _ = self.get_video_info(video_path)
            max_dimension = max(max_dimension, width, height)
        
        self.target_size = (max_dimension, max_dimension)
        return self.target_size
    
    def get_sorted_videos(self):
        """Get list of videos sorted by creation date."""
        videos = []
        for file in self.input_folder.glob('*'):
            if file.suffix.lower() in ['.mp4', '.mov', '.avi']:  # Add more extensions if needed
                creation_date = self.get_creation_date(file)
                videos.append((file, creation_date))
        return sorted(videos, key=lambda x: x[1])
    
    def add_date_overlay(self, video_path, date, output_path):
        """Add date overlay to video and pad to target size."""
        cap = cv2.VideoCapture(str(video_path))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Calculate padding
        target_w, target_h = self.target_size
        x_offset = (target_w - width) // 2
        y_offset = (target_h - height) // 2
        
        # Create VideoWriter with original fps
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, self.target_size)
        
        # Calculate text position (bottom left)
        date_str = date.strftime('%Y-%m-%d')
        text_size = cv2.getTextSize(date_str, self.font, self.font_scale, self.font_thickness)[0]
        text_x = 10  # Padding from left
        text_y = target_h - 10  # Padding from bottom
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Create black background
            padded_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            
            # Overlay original frame
            padded_frame[y_offset:y_offset+height, x_offset:x_offset+width] = frame
            
            # Add date text
            cv2.putText(padded_frame, date_str, (text_x, text_y), 
                       self.font, self.font_scale, self.font_color, self.font_thickness)
            
            out.write(padded_frame)
        
        cap.release()
        out.release()
    
    def process_videos(self, output_path):
        """Process all videos and create final output."""
        try:
            sorted_videos = self.get_sorted_videos()
            if not sorted_videos:
                raise ValueError("No videos found in input folder")
            
            # Determine target size based on largest video
            self.determine_target_size(sorted_videos)
            
            processed_videos = []
            current_date = None
            
            # Process each video
            for i, (video_path, creation_date) in enumerate(sorted_videos):
                print(f"Processing video {i+1}/{len(sorted_videos)}: {video_path.name}")
                video_date = creation_date.date()
                temp_output = self.temp_dir / f"processed_{i}.mp4"
                
                if video_date != current_date:
                    self.add_date_overlay(video_path, creation_date, temp_output)
                    current_date = video_date
                else:
                    # Still need to process for consistent size
                    self.add_date_overlay(video_path, creation_date, temp_output)
                
                processed_videos.append(temp_output)
            
            # Create concat file with input fps
            concat_file = self.temp_dir / 'concat.txt'
            with open(concat_file, 'w') as f:
                for video in processed_videos:
                    f.write(f"file '{video}'\n")
            
            # Concatenate all videos while preserving original fps
            subprocess.run([
                'ffmpeg', '-y',  # Overwrite output if exists
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264',  # Use H.264 codec
                '-preset', 'medium',  # Balance between encoding speed and quality
                '-crf', '23',  # Constant Rate Factor (18-28 is good, lower is better quality)
                str(output_path)
            ], check=True)
            
            print(f"Successfully created output video: {output_path}")
            
        finally:
            # Cleanup temporary files
            for file in self.temp_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    print(f"Error deleting temporary file {file}: {e}")
            try:
                self.temp_dir.rmdir()
            except Exception as e:
                print(f"Error deleting temporary directory: {e}")

def main():
    """
    Main function to process videos.
    
    Before running, ensure you have the required dependencies installed:
    1. Install Python requirements: pip install -r requirements.txt
    2. Install ffmpeg:
       - Ubuntu/Debian: sudo apt-get install ffmpeg
       - macOS: brew install ffmpeg
       - Windows: Download from ffmpeg.org or use: choco install ffmpeg
    """
    import argparse
    import numpy as np  # Required for creating black background
    
    parser = argparse.ArgumentParser(description='Process and concatenate videos with date overlays.')
    parser.add_argument('input_folder', help='Path to the folder containing input videos')
    parser.add_argument('output_path', help='Path for the output video file')
    
    args = parser.parse_args()
    
    processor = VideoProcessor(args.input_folder)
    processor.process_videos(args.output_path)

if __name__ == "__main__":
    main()

