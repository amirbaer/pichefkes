#!/usr/bin/env python3.12

import os
import cv2
import subprocess
from datetime import datetime
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
        
    def get_creation_date(self, file_path):
        """Get creation date of a file."""
        return datetime.fromtimestamp(os.path.getctime(file_path))
    
    def get_sorted_videos(self):
        """Get list of videos sorted by creation date."""
        videos = []
        for file in self.input_folder.glob('*.mp4'):  # Add more extensions if needed
            creation_date = self.get_creation_date(file)
            videos.append((file, creation_date))
        return sorted(videos, key=lambda x: x[1])
    
    def add_date_overlay(self, video_path, date, output_path):
        """Add date overlay to video."""
        cap = cv2.VideoCapture(str(video_path))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Calculate text position (bottom left)
        date_str = date.strftime('%Y-%m-%d')
        text_size = cv2.getTextSize(date_str, self.font, self.font_scale, self.font_thickness)[0]
        text_x = 10  # Padding from left
        text_y = height - 10  # Padding from bottom
        
        # Process video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Add date text
            cv2.putText(frame, date_str, (text_x, text_y), 
                       self.font, self.font_scale, self.font_color, self.font_thickness)
            
            out.write(frame)
        
        cap.release()
        out.release()
        
    def create_concat_file(self, video_list):
        """Create a text file listing all videos to concatenate."""
        concat_file = self.temp_dir / 'concat.txt'
        with open(concat_file, 'w') as f:
            for video in video_list:
                f.write(f"file '{video}'\n")
        return concat_file
    
    def process_videos(self, output_path):
        """Process all videos and create final output."""
        try:
            sorted_videos = self.get_sorted_videos()
            if not sorted_videos:
                raise ValueError("No videos found in input folder")
            
            processed_videos = []
            current_date = None
            
            # Process each video
            for i, (video_path, creation_date) in enumerate(sorted_videos):
                video_date = creation_date.date()
                temp_output = self.temp_dir / f"processed_{i}.mp4"
                
                # Add date overlay if date changed
                if video_date != current_date:
                    self.add_date_overlay(video_path, creation_date, temp_output)
                    current_date = video_date
                else:
                    # Just copy the video if date hasn't changed
                    subprocess.run(['ffmpeg', '-i', str(video_path), '-c', 'copy', str(temp_output)],
                                check=True, capture_output=True)
                
                processed_videos.append(temp_output)
            
            # Create concat file
            concat_file = self.create_concat_file(processed_videos)
            
            # Concatenate all videos
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                str(output_path)
            ], check=True, capture_output=True)
            
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Process and concatenate videos with date overlays.')
    parser.add_argument('input_folder', help='Path to the folder containing input videos')
    parser.add_argument('output_path', help='Path for the output video file')
    
    args = parser.parse_args()
    
    processor = VideoProcessor(args.input_folder)
    processor.process_videos(args.output_path)

if __name__ == "__main__":
    main()
