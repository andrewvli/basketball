"""
Example usage:
    python extract_clips.py --url https://www.youtube.com/watch?v=1_bcliaCXBI --prefix clip
    python extract_clips.py --url https://www.youtube.com/watch?v=1_bcliaCXBI --prefix clip \
            --threshold 40.0 --video_dir videos --clip_dir clips
"""

import yt_dlp
from pathlib import Path
import argparse
import cv2
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector, AdaptiveDetector
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
    # min_scene_len merges sub-3s "scenes" into the previous one, which collapses
    # the spurious cut-and-cut-back pairs caused by camera flashes / bright frames.
    # Compute dynamically from the video's actual frame rate so the 3s floor holds
    # regardless of whether the source is 24, 30, 50, or 60 fps.
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()
    min_scene_len = int(fps * 3)  # 3 seconds worth of frames
    print(f'Detected {fps:.2f} fps → min_scene_len={min_scene_len} frames')

    # Down-weight luma heavily: camera flashes are pure luma events with little
    # hue/sat change, so reducing delta_lum to 0.2 makes the detector nearly
    # blind to brightness spikes while still catching real shot changes (which
    # alter hue and saturation too). Defaults are (hue=1.0, sat=1.0, lum=1.0, edges=0.0).
    flash_tolerant_weights = ContentDetector.Components(
        delta_hue=1.0,
        delta_sat=1.0,
        delta_lum=0.2,
        delta_edges=0.0,
    )

    # Use only AdaptiveDetector: it normalises against a rolling average, making
    # it naturally robust to isolated bright frames. ContentDetector (removed) is
    # more trigger-happy on single-frame anomalies and was adding false cuts.
    # Flash resistance comes from delta_lum=0.2 and min_scene_len,
    # min_content_val=15.0 (default) to catch real cuts without being restrictive.
    scene_manager = SceneManager()
    scene_manager.add_detector(AdaptiveDetector(
        adaptive_threshold=3.5,
        min_content_val=15.0,
        min_scene_len=min_scene_len,
        weights=flash_tolerant_weights,
    ))

    # detect scenes
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    # post-filter: discard any scene shorter than MIN_CLIP_SECS regardless of
    # what the detector decided, so no sub-3s clips are ever written to disk.
    MIN_CLIP_SECS = 3.0
    before = len(scene_list)
    scene_list = [s for s in scene_list if (s[1] - s[0]).get_seconds() >= MIN_CLIP_SECS]
    print(f'Post-filter removed {before - len(scene_list)} clips under {MIN_CLIP_SECS}s '
          f'({len(scene_list)} remaining).')

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