"""
Example usage:
    python rename_clips.py --prefix pnr
    python rename_clips.py --prefix pnr --dir clips
"""

from pathlib import Path
import os
import argparse

def renameClips(dir, prefix):
    """
    Renames clips in the specified directory with the given prefix (e.g. 'pnr_0001, pnr_0002, ...').

    Returns:
        int: Total videos in directory.
    """
    total = 0

    directory = Path(dir)
    videos = sorted(list(directory.glob("*.mp4")))
    total = len(videos)

    for i, video_file in enumerate(videos):
        new_name = f'{prefix}_{i:05d}.mp4'
        new_path = directory / new_name
        video_file.rename(new_path)

    return total

def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prefix",
        required=True,
        help="prefix for clips"
    )

    parser.add_argument(
        "--dir",
        default='clips',
        help="clip directory"
    )

    return parser.parse_args()


def main():
    args = parseArgs()
    total = renameClips(args.dir, args.prefix)
    print(f'{total} clips renamed with prefix {args.prefix}.')

if __name__ == "__main__":
    main()