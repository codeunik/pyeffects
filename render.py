import multiprocessing as mp
import threading
import subprocess as sp
import os

# from wand.image import Image
# import cairosvg
from .elements.place import Place
from pyeffects import g, Frame, FrameConfig

import cv2
import numpy as np
import tqdm
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from multiprocessing import Queue, cpu_count

class Renderer:
    count = -1

    def __init__(self, timeline, frame_size=(1920, 1080), clearall=False, create_png=True):
        self.timeline = timeline
        self.ffmpeg_bin = "/usr/bin/ffmpeg"
        self.frame_size = frame_size
        self.n_drivers = cpu_count()
        self.create_png = create_png
        if self.create_png:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless=new")
            service = Service(executable_path= r"/home/partha/chromedriver")
            self.drivers = []
            for _ in range(self.n_drivers):
                self.drivers.append(webdriver.Chrome(service=service, options=chrome_options))
                self.drivers[-1].set_window_size(5000, 5000)
                self.send(self.drivers[-1], "Emulation.setDefaultBackgroundColorOverride", {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}})

        Renderer.count += 1
        os.system("mkdir -p videos && mkdir -p svgs && mkdir -p pngs")
        if clearall:
            os.system("rm -rf videos/* && rm -rf svgs/* && rm -rf pngs/*")
        os.system(f"mkdir -p svgs/{Renderer.count} && mkdir -p pngs/{Renderer.count}")

    def render_video(self, save_frames={-1: True}):

        frame_number = 0
        threads = [None for _ in range(self.n_drivers)]
        frame_queue = Queue()

        while frame_number <= self.timeline._lifetime:
            print(
                f"creating frame: {frame_number} | completed: {(frame_number / self.timeline._lifetime) * 100:.2f}%",
                end="\r",
            )
            frame = Frame(*self.frame_size)
            self.timeline.exec(frame_number)

            # for k, v in (
            #     pd.json_normalize(g, sep=".").to_dict(orient="records")[0].items()
            # ):
            for k, v in g.items():
                if k not in g._blacklisted:
                    if issubclass(type(v), Place):
                        frame.add(v)

            svg_data = frame.generate().encode()
            
            finished = frame_number == self.timeline._lifetime
            if threads[frame_number%self.n_drivers] is None:
                frame_queue.put([frame, frame_number, save_frames, finished])
                p = threading.Thread(
                    target=self.save_svg, args=(frame_queue, frame_number%self.n_drivers)
                )
                threads[frame_number%self.n_drivers] = p
                p.start()
            else:
                frame_queue.put([frame, frame_number, save_frames, finished])
            
            

            for element in frame.elements.values():
                element.dynamic_reset()
                try:
                    for element in element.get_mask().elements:
                        element.dynamic_reset()
                except:
                    pass

            frame_number += 1
        
        for c, th in enumerate(threads):
            th.join()

        frame_queue.get()
        

    def save_svg(self, frame_queue, driver_idx):
        while True:
            frame, frame_number, save_frames, finished = frame_queue.get()
            
            if finished:
                frame_queue.put([frame, frame_number, save_frames, finished])
                if self.create_png:
                    driver = self.drivers[driver_idx]
                    self.send(driver, "Emulation.setDefaultBackgroundColorOverride")
                    driver.quit()
                break
            if save_frames.get(-1):
                svg_path = f"svgs/{Renderer.count}/{str(frame_number).zfill(8)}.svg"
            elif save_frames.get(frame_number, False):
                svg_path = f"svgs/{Renderer.count}/{frame_number}.svg"
            
            frame.save(svg_path)
            svg_abs_path = os.path.abspath(svg_path)

            if self.create_png:
                driver = self.drivers[driver_idx]
                driver.get('file://' + svg_abs_path)
                e = driver.find_element(by=By.TAG_NAME, value='svg')
                e.screenshot(f'pngs/{Renderer.count}/{str(frame_number).zfill(8)}.png')
                

    def send(self, driver, cmd, params={}):
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd':cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')


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
