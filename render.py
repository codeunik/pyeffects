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
                             "-crf", "0", \
                             "-preset", "ultrafast" if preview else "slower", \
                             "-pix_fmt", "yuv420p",\
                             "-threads", "10",\
                             "-an",
                             "-tune", "animation",\
                             "-loglevel", "error",\
                             f"{filename}.mp4"]), stdin=PIPE)

    def save_frame_and_convert(self, frame, frame_number):
        frame.save(f"img/{frame_number}.svg")
        os.system(f"convert img/{frame_number}.svg img/png/{frame_number}.png && mv img/{frame_number}.svg img/svg/")

    def render(self):
        os.system("mkdir -p img/svg && rm -rf img/svg/* && mkdir -p img/png && rm -rf img/png/*")
        frame_number = 0
        pipe_png_start_flag = True
        while frame_number <= self.timeline._lifetime:
            print(f"{frame_number}, {(frame_number/self.timeline._lifetime)*100:.2f}%", end="\r")
            frame = Frame(self.width, self.height)
            self.timeline.exec(frame_number, frame)
            p = mp.Process(target=self.save_frame_and_convert, args=(frame,frame_number))
            p.start()

            if pipe_png_start_flag:
                mp.Process(target=self.pipe_png, args=(0, )).start()
                pipe_png_start_flag = False

            for element in frame.elements.values():
                element.dynamic_reset()

            frame_number += 1


    def pipe_png(self, i):
        if self.bool_save_video:
            self.p.stdin.write(Popen(["cat", f"img/png/{i}.png"], stdout=PIPE).stdout.read())

        if not self.bool_save_frames:
            os.system(f"rm img/png/{i}.png && rm img/svg/{i}.svg")

        if i < self.timeline._lifetime:
            while not os.path.exists(f"img/png/{i+1}.png"):
                pass
            self.pipe_png(i+1)

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
    # "-crf", "18",\
    # "-preset", "ultrafast" if preview else "slower",\

    #"-frames:v", f"{number_of_svgs}",\
    # "-c:a","aac",\
    # "-q:a","1",\
    # "-ac","2",\
    # "-ar","48000",\

    # parallel convert '{} {.}.png' ::: *.svg

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
