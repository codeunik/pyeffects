import multiprocessing as mp
import threading
import subprocess as sp
import os

# from wand.image import Image
# import cairosvg
from .elements.place import Place
from pyeffects import g, Frame
import tempfile
import pandas as pd
import time

import cv2
import numpy as np
import tqdm

class Renderer:
    count = -1

    def __init__(self, timeline, preview=True, clearall=False):
        self.timeline = timeline
        self.width = 640 if preview else 1920
        self.height = 360 if preview else 1080
        self.preview = preview
        self.ffmpeg_bin = "/usr/bin/ffmpeg"
        Renderer.count += 1
        os.system("mkdir -p videos && mkdir -p svgs && mkdir -p pngs")
        if clearall:
            os.system("rm -rf videos/* && rm -rf svgs/* && rm -rf pngs/*")
        os.system(f"mkdir -p svgs/{Renderer.count} && mkdir -p pngs/{Renderer.count}")

    def render_video(
        self, filename="mov", video=False, save_frames={-1: True}, png=1, svg=0
    ):
        if video:
            video_writer = cv2.VideoWriter(f"videos/{filename}_{Renderer.count}.avi",cv2.VideoWriter_fourcc(*'DIVX'), self.timeline.fps, (self.width, self.height))
            procs = []
            n_procs = 100
            manager = mp.Manager()
            rendered_pngs = manager.dict()

        frame_number = 0
        while frame_number <= self.timeline._lifetime:
            print(
                f"creating frame: {frame_number} | completed: {(frame_number / self.timeline._lifetime) * 100:.2f}%",
                end="\r",
            )
            frame = Frame(self.width, self.height)
            self.timeline.exec(frame_number)

            for k, v in (
                pd.json_normalize(g, sep=".").to_dict(orient="records")[0].items()
            ):
                if issubclass(type(v), Place):
                    frame.add(v)

            svg_data = frame.generate().encode()
            if video:
                p = mp.Process(
                    target=self.parallel_videopng, args=(svg_data, rendered_pngs)
                )
                procs.append(p)
                p.start()
                time.sleep(0.001)

                if (len(procs) == n_procs) or ((frame_number == self.timeline._lifetime) and (self.timeline._lifetime % n_procs)):
                    for p in tqdm.tqdm(procs):
                        p.join()
                    
                    for _, png_data in sorted(rendered_pngs.items(), key=lambda x: x[0]):
                        png_data = cv2.imdecode(np.frombuffer(png_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                        video_writer.write(png_data)
                    
                    procs.clear()
                    rendered_pngs.clear()

            elif png:
                p = mp.Process(
                    target=self.parallel_svg2png, args=(svg_data, frame_number)
                )
                p.start()

            # with io.StringIO() as svg_file:
            #     svg_file.write(frame.generate())
            # with tempfile.NamedTemporaryFile() as tmp_svg_file:
            #     tmp_svg_file.write(frame.generate().encode())
            # with Image(blob=frame.generate().encode()) as img:
            #     img.format = 'png'
            #     img.save(pipe.stdin)
            # pipe.stdin.write(frame.generate().encode())

            # cairosvg.svg2png(frame.generate(), unsafe=True, write_to=pipe.stdin)

            if svg:
                p = threading.Thread(
                    target=self.save_svg, args=(frame, frame_number, save_frames)
                )
                p.start()

            for element in frame.elements.values():
                element.dynamic_reset()
                try:
                    for element in element.get_mask().elements:
                        element.dynamic_reset()
                except:
                    pass

            frame_number += 1

        if video:
            video_writer.release()

    def parallel_videopng(self, svg_data, render_pngs):
        start_time = time.time()
        convert_svg_2_png = sp.Popen(
            ["inkscape", "-p", "--export-type=png"],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        png_data, error_message = convert_svg_2_png.communicate(input=svg_data)
        render_pngs[start_time] = png_data

    def parallel_svg2png(self, svg_data, frame_number):
        convert_svg_2_png = sp.Popen(
            [
                "inkscape",
                "-p",
                f"--export-filename=pngs/{Renderer.count}/{str(frame_number).zfill(8)}.png",
            ],
            stdin=sp.PIPE,
            # stdout=sp.PIPE,
            stderr=sp.PIPE,
        )

        _ = convert_svg_2_png.communicate(input=svg_data)

        # with open(f'pngs/{Renderer.count}/{str(frame_number).zfill(8)}.png', 'wb') as f:
        #     f.write(png_data)

    def save_svg(self, frame, frame_number, save_frames):
        if save_frames.get(-1):
            frame.save(f"svgs/{Renderer.count}/{str(frame_number).zfill(8)}.svg")
        elif save_frames.get(frame_number, False):
            frame.save(f"svgs/{Renderer.count}/{frame_number}.svg")


    # def render_video(self, filename="mov", lossless=False, remove_images=False):
    #     #if len(os.listdir(f"svgs/{Renderer.count}")) == 0:
    #     self.render_svgs()
    #     os.system(f'cd svgs/{Renderer.count} && mv **/* . ')
    #     os.system(f'cd svgs/{Renderer.count} && rm -r */')

    #     if lossless:
    #         os.system(f"cd svgs/{Renderer.count} && "
    #                   f"{self.ffmpeg} -framerate {self.timeline.fps} "
    #                   f"-i %d.svg -c:v copy {filename}.mkv && "
    #                   f"mv {filename}.mkv ../../videos/")
    #     else:
    #         os.system(" ".join([f"cd svgs/{Renderer.count} &&",
    #                             self.ffmpeg,
    #                             "-y",
    #                             #"-vcodec", "png",
    #                             "-framerate", f"{self.timeline.fps}",
    #                             "-s", f"{self.width}x{self.height}",
    #                             "-i", "%d.svg",
    #                             "-c:v", "libx264",
    #                             "-crf", "0" if self.preview else "17",
    #                             "-preset", "ultrafast" if self.preview else "slower",
    #                             "-pix_fmt", "yuv420p",
    #                             "-an",
    #                             "-tune", "animation",
    #                             f"{filename}.mp4",
    #                             f"&& mv {filename}.mp4 ../../videos/"]))
    #     if remove_images:
    #         os.system(f"rm -rf svgs/{Renderer.count}")

    # def render_svgs(self):
    #     frame_number = 0
    #     processes = []
    #     while frame_number <= self.timeline._lifetime:
    #         print(
    #             f"creating frame: {frame_number} | completed: {(frame_number / self.timeline._lifetime) * 100:.2f}%",
    #             end="\r")
    #         frame = Frame(self.width, self.height)
    #         self.timeline.exec(frame_number, frame)

    #         dir = str(frame_number)[:-2]
    #         os.system(f"mkdir -p svgs/{Renderer.count}/{dir if dir else '0'}")
    #         p = mp.Process(target=frame.save, args=(f"svgs/{Renderer.count}/{dir if dir else '0'}/{frame_number}.svg",))
    #         processes.append(p)
    #         p.start()

    #         if len(processes) == 256:
    #             for p in processes:
    #                 p.join()
    #             processes.clear()

    #         for element in frame.elements.values():
    #             element.dynamic_reset()

    #         frame_number += 1

    #     for p in processes:
    #         p.join()
    #     processes.clear()

    # " DRI_PRIME=1 parallel convert '{} {.}.bmp' ::: *.svg &&"
    # " mv *.bmp ../bmps &&"
    # " cd ../bmps &&"
    # "-vb", "20M",\
    # "-start_number", "0",\
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

    # "-frames:v", f"{number_of_svgs}",\
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
    #
    #     if self.bool_save_video:
    #         self.p = Popen((["ffmpeg",
    #                          "-y",
    #                          "-f", "image2pipe",\
    #                          "-vcodec", "png",\
    #                          "-framerate", f"{self.timeline.fps}",\
    #                          "-s", f"{self.width}x{self.height}",\
    #                          "-i", "%d.png",\
    #                          "-c:v", "libx264",\
    #                          "-crf", "0", \
    #                          "-preset", "ultrafast" if preview else "slower", \
    #                          "-pix_fmt", "yuv420p",\
    #                          "-an",
    #                          "-tune", "animation",\
    #                          "-loglevel", "error",\
    #                          f"{filename}.mp4"]), stdin=PIPE)
