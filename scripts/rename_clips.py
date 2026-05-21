"""
Example usage:
    python rename_clips.py --prefix pnr
    python rename_clips.py --prefix pnr --dir clips --shuffle False
"""

from pathlib import Path
import os
import argparse
import random

def renameClips(dir, prefix, shuffle):
    """
    Renames clips in the specified directory with the given prefix (e.g. 'pnr_0001, pnr_0002, ...').
    Option to shuffle the clips, so that the last n can be deleted when balancing class sizes.

    Returns:
        int: Total videos in directory.
    """
    total = 0

    directory = Path(dir)
    videos = list(directory.glob("*.mp4"))
    if shuffle:
        random.shuffle(videos)
    else:
        videos = sorted(videos)
    total = len(videos)

    # temporary names to avoid overwriting
    temp_paths = []
    for i, video in enumerate(videos):
        temp = directory / f"__tmp_{i}.mp4"
        video.rename(temp)
        temp_paths.append(temp)

    # final names
    for i, temp in enumerate(temp_paths, start=1):
        final = directory / f"{prefix}_{i:05d}.mp4"
        temp.rename(final)

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

    parser.add_argument(
        "--shuffle",
        default=True,
        help="whether or not to shuffle clips"
    )

    return parser.parse_args()


def main():
    args = parseArgs()
    total = renameClips(args.dir, args.prefix, args.shuffle)
    print(f'{total} clips renamed with prefix {args.prefix}.')

if __name__ == "__main__":
    main()