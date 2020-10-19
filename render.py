import multiprocessing as mp
import os
from .elements.frame import Frame
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading


class Renderer:
    count = -1

    def __init__(self, timeline, preview=True, clearall=False):
        self.timeline = timeline
        self.width = 640 if preview else 1920
        self.height = 360 if preview else 1080
        self.preview = preview
        Renderer.count += 1

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.drivers = [webdriver.Chrome(chrome_options=chrome_options) for _ in range(mp.cpu_count())]
        # set viewport to be the image size
        for i in range(len(self.drivers)):
            window_size = self.drivers[i].execute_script(
                """
                return [window.outerWidth - window.innerWidth + arguments[0],
                  window.outerHeight - window.innerHeight + arguments[1]];
                """, self.width, self.height)
            self.drivers[i].set_window_size(*window_size)
        self.cwd = os.getcwd()
        if clearall:
            os.system(
                "mkdir -p videos && rm -rf videos/* "
                "&& mkdir -p images/svgs && rm -rf images/svgs/* "
                "&& mkdir -p images/pngs && rm -rf images/pngs/* "
            )
        os.system(f"mkdir -p images/svgs/{Renderer.count} && mkdir -p images/pngs/{Renderer.count}")

    def render_svgs(self):
        frame_number = 0
        processes = []
        while frame_number <= self.timeline._lifetime:
            print(
                f"creating frame: {frame_number} | completed: {(frame_number / self.timeline._lifetime) * 100:.2f}%",
                end="\r")
            frame = Frame(self.width, self.height)
            self.timeline.exec(frame_number, frame)

            p = mp.Process(target=frame.save, args=(f"images/svgs/{Renderer.count}/{frame_number}.svg",))
            p.start()
            processes.append(p)

            if len(processes) == 64:
                for p in processes:
                    p.join()
                processes.clear()

            for element in frame.elements.values():
                element.dynamic_reset()

            frame_number += 1

        for p in processes:
            p.join()
        processes.clear()

    def render_pngs(self, remove_svgs=False):
        if len(os.listdir(f"images/svgs/{Renderer.count}")) == 0:
            self.render_svgs()
        q = mp.Queue(maxsize=mp.cpu_count())
        threads = []
        for i in range(mp.cpu_count()):
            q.put(i)
        frame_number = 0
        while frame_number < len(os.listdir(f"images/svgs/{Renderer.count}")):
            if not q.empty():
                t = threading.Thread(target=self._save_png, args=(frame_number, q))
                threads.append(t)
                t.start()
                frame_number += 1

        for t in threads:
            t.join()

        for i in range(mp.cpu_count()):
            self.drivers[i].quit()

        if remove_svgs:
            os.system(f"rm -rf images/svgs/{Renderer.count}")

    def render_video(self, filename="mov", lossless=False, remove_images=False):
        if len(os.listdir(f"images/pngs/{Renderer.count}")) == 0:
            self.render_pngs()

        if lossless:
            os.system(f"cd images/pngs/{Renderer.count} && "
                      f"ffmpeg -framerate {self.timeline.fps} "
                      f"-i %d.png -c:v copy {filename}.mkv && "
                      f"mv {filename}.mkv ../../../videos/")
        else:
            os.system(" ".join([f"cd images/pngs/{Renderer.count} &&",
                                "ffmpeg",
                                "-y",
                                "-vcodec", "png",
                                "-framerate", f"{self.timeline.fps}",
                                "-s", f"{self.width}x{self.height}",
                                "-i", "%d.png",
                                "-c:v", "libx264",
                                "-crf", "0" if self.preview else "17",
                                "-preset", "ultrafast" if self.preview else "slower",
                                "-pix_fmt", "yuv420p",
                                "-an",
                                "-tune", "animation",
                                f"{filename}.mp4",
                                f"&& mv {filename}.mp4 ../../../videos/"]))
        if remove_images:
            print("ok")
            os.system(f"rm -rf images/svgs/{Renderer.count} && rm -rf images/pngs/{Renderer.count}")

    def _save_png(self, frame_number, q):
        i = q.get()
        self.drivers[i].get("file://" + self.cwd + f"/images/svgs/{Renderer.count}/{frame_number}.svg")
        self.drivers[i].save_screenshot(self.cwd + f"/images/pngs/{Renderer.count}/{frame_number}.png")
        q.put(i)

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
