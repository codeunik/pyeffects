import multiprocessing as mp
import os
from .elements.frame import Frame
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading

class Renderer:
    def __init__(self, timeline, preview=True, filename="mov", save_pngs=True, save_video=False):
        self.timeline = timeline
        self.width = 640 if preview else 1920
        self.height = 360 if preview else 1080
        self.preview = preview
        self.filename = filename
        self.bool_save_pngs = save_pngs
        self.bool_save_video = save_video and self.bool_save_pngs
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

    def render(self):
        os.system("mkdir -p mov && rm -rf mov/* && mkdir -p img/svg && rm -rf img/svg/* && mkdir -p img/png && rm -rf img/png/*")
        frame_number = 0
        processes = []
        while frame_number <= self.timeline._lifetime:
            print(f"complete: {(frame_number/self.timeline._lifetime)*100:.2f}%")
            print(f"creating frame: {frame_number}")
            frame = Frame(self.width, self.height)
            self.timeline.exec(frame_number, frame)
            p = mp.Process(target=frame.save, args=(f"img/svg/{frame_number}.svg",))
            p.start()
            processes.append(p)

            for element in frame.elements.values():
                element.dynamic_reset()

            if len(processes) == 256:
                for p in processes:
                    p.join()
                processes.clear()

            frame_number += 1

        for p in processes:
            p.join()
        processes.clear()

        if self.bool_save_pngs:
            q = mp.Queue(maxsize=mp.cpu_count())
            threads = []
            for i in range(mp.cpu_count()):
                q.put(i)
            frame_number = 0
            while frame_number <= self.timeline._lifetime:
                if not q.empty():
                    t = threading.Thread(target=self.save_png, args=(frame_number, q))
                    threads.append(t)
                    t.start()
                    frame_number += 1

            for t in threads:
                t.join()

        for i in range(mp.cpu_count()):
            self.drivers[i].quit()

        if self.bool_save_video:
            os.system(" ".join(["cd img/png &&",
                                "ffmpeg",
                                "-y",
                                "-vcodec", "png",
                                "-i", "%d.png",
                                "-c:v", "libx264",
                                "-crf", "0" if self.preview else "17",
                                "-preset", "ultrafast" if self.preview else "slower",
                                "-pix_fmt", "yuv420p",
                                "-an",
                                "-tune", "animation",
                                f"{self.filename}.mp4",
                                f"&& mv {self.filename}.mp4 ../../mov/"]))

    def save_png(self, frame_number, q):
        i = q.get()
        self.drivers[i].get("file://"+self.cwd+f"/img/svg/{frame_number}.svg")
        self.drivers[i].save_screenshot(self.cwd+f"/img/png/{frame_number}.png")
        q.put(i)


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
