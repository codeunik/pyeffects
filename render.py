import base64
import multiprocessing as mp
import os
from subprocess import PIPE, Popen

from .elements.frame import Frame


class Renderer:
    def __init__(self, timeline, preview=True, filename="mov", save_video=True, save_frames=False):
        self.timeline = timeline
        self.width = 640 if preview else 1920
        self.height = 360 if preview else 1080
        self.bool_save_frames = save_frames
        self.bool_save_video = save_video
        if self.bool_save_video:
            self.p = Popen((["ffmpeg",
                             "-y",
                             "-f", "image2pipe",\
                             "-vcodec", "png",\
                             "-framerate", f"{self.timeline.fps}",\
                             "-s", f"{self.width}x{self.height}",\
                             "-i", "-",\
                             "-c:v", "libx264",\
                             "-crf", "0",\
                             "-preset", "veryfast",\
                             "-pix_fmt", "yuv420p",\
                             "-threads", "10",\
                             "-an",
                             #"-loglevel", "error",\
                             f"{filename}.mp4"]), stdin=PIPE)

    def render(self):
        os.system("mkdir -p img/svg && rm -rf img/svg/* && mkdir -p img/png && rm -rf img/png/*")
        frame_number = 0
        processes = []
        while frame_number <= self.timeline._lifetime:
            print(f"{frame_number}, {(frame_number/self.timeline._lifetime)*100:.2f}%", end="\r")
            frame = Frame(self.width, self.height)
            self.timeline.exec(frame_number, frame)
            p = mp.Process(target=frame.save, args=(f"img/svg/{frame_number}.svg", ))
            processes.append(p)
            p.start()
            if len(processes) == 256:
                for p in processes:
                    p.join()
                processes.clear()
                self.pipe_png(frame_number, 256)

            for element in frame.elements.values():
                element.dynamic_reset()

            frame_number += 1

        for p in processes:
            p.join()
        self.pipe_png(self.timeline._lifetime, len(processes))
        os.system(
            "mkdir -p img/frames/ && mv img/png img/frames && cd img/frames && find . -type f -print0 | xargs -0 -I file mv --backup=numbered file . && rm -rf png"
        )

    def pipe_png(self, last_frame_number, number_of_frames):
        first_frame_number = last_frame_number - number_of_frames + 1
        os.system(f"mkdir -p img/lot/{first_frame_number} && mkdir -p img/png/{first_frame_number} && cd img && "\
                  f"mv svg/{{{first_frame_number}..{last_frame_number}}}.svg lot/{first_frame_number}/ && "\
                  f"cd lot/{first_frame_number} && "\
                  "parallel convert '{} {.}.png' ::: *.svg && "\
                  f"mv *.png ../../png/{first_frame_number}")
        for i in range(first_frame_number, last_frame_number + 1):
            if self.bool_save_video:
                self.p.stdin.write(
                    Popen(["cat", f"img/png/{first_frame_number}/{i}.png"],
                          stdout=PIPE).stdout.read())
            if not self.bool_save_frames:
                os.system(
                    f"rm img/png/{first_frame_number}/{i}.png && rm img/lot/{first_frame_number}/{i}.svg"
                )

    # " DRI_PRIME=1 parallel convert '{} {.}.bmp' ::: *.svg &&"
    # " mv *.bmp ../bmps &&"
    # " cd ../bmps &&"
    #"-vb", "20M",\
    #"-start_number", "0",\
    # "-i", "-",\
    # "-bf", "2",\
    # "-g", "30",\
    # "-an",
    # "-use_editlist", "0",\
    # "-movflags", "+faststart",\
    # "-profile:v", "high",\
    # "-tune", "animation",\
    # "-preset", "ultrafast" if preview else "slower",\

    #"-frames:v", f"{number_of_svgs}",\
    # "-c:a","aac",\
    # "-q:a","1",\
    # "-ac","2",\
    # "-ar","48000",\

    # def concat_partials(self):
    #     if self.bool_combine_partial_renders:
    #         mov_files = []
    #         for mov in sorted(os.listdir("mov"), key=lambda x: int(x[:-4])):
    #             mov_files.append(f"file '{mov}'")
    #         with open("mov/movlist.txt", "w") as f:
    #             f.write("\n".join(mov_files))
    #         os.system(" ".join(["cd mov &&", self.ffmpeg_bin,
    #                             "-safe", "0",\
    #                             "-f", "concat",\
    #                             "-i", "movlist.txt",\
    #                             "-c", "copy",\
    #                             "-loglevel", "error",\
    #                             "mov.mp4"]))
