#!/usr/local/bin/python3

import os
import sys
import librosa
import moviepy.editor as mpy
import tqdm

def create_video(audio_file, frame_folder, output_file):
    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Detect the beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # Get the list of frame files
    frame_files = sorted([os.path.join(frame_folder, f) for f in os.listdir(frame_folder) if f.endswith('.png')])

    # Repeat or truncate the frame files list to match the number of beats
    while len(frame_files) < len(beat_times):
        frame_files += frame_files
    frame_files = frame_files[:len(beat_times)]

    # Create a clip for each frame, with the duration set to the time until the next beat
    clips = []
    for i in tqdm.tqdm(range(len(frame_files) - 1), desc="generating"):
        img = mpy.ImageClip(frame_files[i], duration=beat_times[i+1] - beat_times[i])
        clips.append(img)

    # Concatenate the clips and set the audio
    video = mpy.concatenate_videoclips(clips)
    video.audio = mpy.AudioFileClip(audio_file)

    # Write the video file
    video.write_videofile(output_file, codec='libx264', fps=29.97)

# Check that the right number of command-line arguments was provided
if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} AUDIO_FILE FRAME_FOLDER OUTPUT_FILE.MP4")
    sys.exit(1)

# Example usage:
create_video(sys.argv[1], sys.argv[2], sys.argv[3])
