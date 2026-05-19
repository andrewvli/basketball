class Pipeline:
    """End-to-end pipeline: video → spatial data for tactile board."""

    def __init__(self, config: dict):
        raise NotImplementedError

    def run(self, video_path: str) -> dict:
        raise NotImplementedError
