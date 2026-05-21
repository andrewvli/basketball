"""
Example usage:
    python extract_clips.py --url https://www.youtube.com/watch?v=1_bcliaCXBI --prefix clip
    python extract_clips.py --url https://www.youtube.com/watch?v=1_bcliaCXBI --prefix clip \
            --threshold 40.0 --video_dir videos --clip_dir clips
"""

import yt_dlp
from pathlib import Path
import argparse
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector, AdaptiveDetector, HashDetector
from scenedetect.video_splitter import split_video_ffmpeg
import time

def getVideoTitle(url):
    """
    This function gets the title of the video at the specified URL.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "logger": None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("title", "video")

def downloadVideo(url, outdir):
    """
    This function downloads a YouTube video at the specified URL and saves
    it as an .mp4 file in the specified out directory.
    """
    title = getVideoTitle(url)
    outpath = Path(f"{outdir}/{title}.mp4")

    if outpath.exists():
        print(f"\n{title} already downloaded.")
    else:
        print(f'\nDownloading video {title}...')
        # ensure parent directory exists
        outpath.parent.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            "outtmpl": str(outpath),
            "merge_output_format": "mp4",
            "no_warnings": True,
            "logger": None,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print('Download complete.')
    return outpath


def splitVideo(video_path, outdir, prefix, threshold=50.0,
):
    """
    This function detects scenes and splits video into clips.
    """
    print('\nSplitting video into clips...')
    start = time.time()
    video_path = Path(video_path)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # open video
    video = open_video(str(video_path))

    # configure scene manager
    scene_manager = SceneManager()
    scene_manager.add_detector(AdaptiveDetector(adaptive_threshold=3.0))
    scene_manager.add_detector(ContentDetector(threshold=75.0)) # higher = ignores flashes

    # detect scenes
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    # split/export scenes
    split_video_ffmpeg(
        input_video_path=str(video_path),
        scene_list=scene_list,
        output_dir=str(outdir),
        output_file_template=f"{prefix}_$SCENE_NUMBER.mp4",
    )
    
    elapsed = time.time() - start
    print(f'Clip detection complete. {len(scene_list)} clips collected in {elapsed:.2f} seconds.')
    return scene_list

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        required=True,
        help="YouTube video URL"
    )

    parser.add_argument(
        "--prefix",
        required=True,
        help="Prefix for output clip filenames"
    )

    parser.add_argument(
        "--threshold",
        default=40,
        help="Threshold for clip detection"
    )

    parser.add_argument(
        "--video_dir",
        default="videos",
        help="Threshold for clip detection"
    )

    parser.add_argument(
        "--clip_dir",
        default="clips",
        help="Threshold for clip detection"
    )

    return parser.parse_args()

def main():
    args = parse_args()
    video_path = downloadVideo(args.url, args.video_dir)
    scene_list = splitVideo(video_path, args.clip_dir, args.prefix, threshold=args.threshold)

if __name__ == "__main__":
    main()