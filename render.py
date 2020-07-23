import math
import os

from .elements.frame import Frame


class Renderer:
    def __init__(self,
                 timeline,
                 width=1920,
                 height=1080,
                 preview=False,
                 save_frames=True,
                 produce_video=True):
        self.timeline = timeline
        self.width = width
        self.height = height
        self.bool_preview = preview
        self.bool_save_frames = save_frames
        self.bool_produce_video = produce_video

    def render(self):
        os.system("mkdir -p svgs && mkdir -p bmps && rm -rf svgs/* && rm -rf bmps/*")
        frame_number = 0
        while frame_number <= self.timeline._lifetime:
            frame = Frame(self.width, self.height)
            self.timeline.exec(frame_number, frame)

            if self.bool_preview:
                self.preview()

            if self.bool_save_frames:
                frame.save(f"svgs/{frame_number}.svg")

            frame_number += 1

        if self.bool_produce_video:
            self._produce_video()

    def preview(self):
        pass

    def _produce_video(self):
        os.system(
            f"cd svgs/ &&"
            " DRI_PRIME=1 ffmpeg"\
            f" -r {self.timeline.fps}"\
            f" -s {self.width}x{self.height}"\
            " -f image2"\
            " -vb 20M"\
            " -start_number 0"\
            " -i %d.svg"\
            " -vcodec libx264"\
            " -crf 18"\
            " -pix_fmt yuv420p"\
            " -an"\
            f" mov.mp4"\
            f" && mv mov.mp4 ../mov/"
        )

        # " DRI_PRIME=1 parallel convert '{} {.}.bmp' ::: *.svg &&"
        # " mv *.bmp ../bmps &&"
        # " cd ../bmps &&"
