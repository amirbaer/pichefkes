#!/usr/bin/env python3.12

import torch
from whisper import load_model
import time
import sys
from tqdm import tqdm
import argparse
from pydub import AudioSegment

def transcribe_with_progress(file_path):
    """Transcribe audio file with progress bar."""
    # Load the model (downloads first time)
    print("Loading Whisper model...")
    model = load_model("base")
    
    print("\nTranscribing...")
    start_time = time.time()
    
    try:
        # Create progress bar without percentage (will show elapsed time instead)
        progress_bar = tqdm(total=None, desc="Processing", unit=" segments")
        
        def progress_callback(progress):
            # Update progress bar position by 1 for each segment
            progress_bar.update(1)
        
        result = model.transcribe(
            file_path,
            language="he",
            verbose=False,  # Reduce console output
            progress_callback=progress_callback
        )
        
        progress_bar.close()
        
        # Calculate and display statistics
        end_time = time.time()
        process_time = end_time - start_time
        
        print(f"\nStats:")
        print(f"Process time: {process_time:.1f} seconds")
        
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

