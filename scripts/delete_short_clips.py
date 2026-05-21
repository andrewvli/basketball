"""
Example usage:
    python delete_short_clips.py
    python delete_short_clips.py --dir ../clips
"""

from pathlib import Path
import cv2
import os
import argparse

def deleteClips(dir, threshold=2):
    """
    Deletes clips in the specified directory below the given threshold (default 2 seconds).

    Returns:
        int: Number of deleted videos.
        int: Total videos in original directory;
    """
    n_deleted = 0
    total = 0

    directory = Path(dir)
    for video_file in directory.glob("*.mp4"):
        cap = cv2.VideoCapture(str(video_file))

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        duration = frames / fps if fps > 0 else 0

        if duration < threshold:
            n_deleted += 1
            os.remove(video_file)

        cap.release()
        total += 1

    return n_deleted, total

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dir",
        default="clips",
        help="Clip directory"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    n_deleted, total = deleteClips(args.dir)
    print(f'{n_deleted} clips deleted out of {total}.')

if __name__ == "__main__":
    main()