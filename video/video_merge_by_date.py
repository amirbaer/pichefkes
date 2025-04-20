#!/usr/bin/env python3.12

import os
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip

# Set the path to the folder containing the videos
video_folder = "path/to/your/video/folder"

# Get a list of all video files in the folder
video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

# Sort the video files by creation date
video_files.sort(key=lambda x: os.path.getctime(os.path.join(video_folder, x)))

# Initialize variables
clips = []
current_date = None

# Iterate through the sorted video files
for video_file in video_files:
    # Get the full path of the video file
    video_path = os.path.join(video_folder, video_file)
    
    # Get the creation date of the video file
    creation_date = datetime.fromtimestamp(os.path.getctime(video_path)).strftime("%Y-%m-%d")
    
    # Load the video clip
    clip = VideoFileClip(video_path)
    
    # If the date has changed, add a text overlay with the new date
    if creation_date != current_date:
        current_date = creation_date
        text_clip = TextClip(current_date, fontsize=24, color="white")
        text_clip = text_clip.set_pos(("left", "bottom")).set_duration(3)
        clip = CompositeVideoClip([clip, text_clip])
    
    # Append the clip to the list of clips
    clips.append(clip)

# Concatenate all the video clips
final_clip = concatenate_videoclips(clips)

# Write the final video to a file
output_path = "output_video.mp4"
final_clip.write_videofile(output_path)
