#!/usr/bin/env python3.12

import torch
from whisper import load_model
import time
import sys
from tqdm import tqdm
import argparse
from pydub import AudioSegment

def get_audio_duration(file_path):
    """Get duration of audio file in seconds."""
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000.0

def transcribe_with_progress(file_path):
    """Transcribe audio file with progress simulation."""
    # Load the model (downloads first time)
    print("Loading Whisper model...")
    model = load_model("base")
    
    # Get audio duration
    duration = get_audio_duration(file_path)
    
    # Start transcription with simulated progress
    start_time = time.time()
    progress_bar = tqdm(total=100, desc="Transcribing", unit="%")
    
    try:
        # Run transcription
        result = model.transcribe(file_path, language="he")
        
        # Simulate progress updates
        for i in range(101):
            time.sleep(duration / 100 / 2)  # Simulate progress proportional to duration
            progress_bar.update(1)
        
        progress_bar.close()
        
        # Calculate and display statistics
        end_time = time.time()
        process_time = end_time - start_time
        speed_factor = duration / process_time
        
        print(f"\nStats:")
        print(f"Audio duration: {duration:.1f} seconds")
        print(f"Process time: {process_time:.1f} seconds")
        print(f"Speed factor: {speed_factor:.1f}x realtime")
        
        print("\nTranscription:")
        print(result["text"])
        
    except Exception as e:
        progress_bar.close()
        print(f"\nError during transcription: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Transcribe an audio file using Whisper')
    parser.add_argument('file', nargs='?', help='Path to the audio file')
    args = parser.parse_args()
    
    if not args.file:
        parser.print_help()
        sys.exit(1)
    
    transcribe_with_progress(args.file)

if __name__ == "__main__":
    main()

