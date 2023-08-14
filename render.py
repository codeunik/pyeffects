import multiprocessing as mp
import subprocess as sp
import os
# from wand.image import Image
# import cairosvg
from .elements.place import Place
from pyeffects import g, b, Frame
import tempfile
import pandas as pd

class Renderer:
    count = -1

    def __init__(self, timeline, preview=True, clearall=False):
        self.timeline = timeline
        self.width = 640 if preview else 1920
        self.height = 360 if preview else 1080
        self.preview = preview
        self.ffmpeg_bin = '/usr/bin/ffmpeg'
        Renderer.count += 1
        os.system("mkdir -p videos && mkdir -p svgs && mkdir -p pngs")
        if clearall:
            os.system(
                "rm -rf videos/* && rm -rf svgs/* && rm -rf pngs/*"
            )
        os.system(f"mkdir -p svgs/{Renderer.count} && mkdir -p pngs/{Renderer.count}")

    def render_video(self, filename="mov", video=False, save_frames={-1:True}, png=1, svg=0):
        if video:
            command = [
                    self.ffmpeg_bin,
                    '-y',
                    '-f', 'image2pipe',
                    '-r', f'{self.timeline.fps}', # frames per second
                    '-pix_fmt', 'rgba',
                    "-s", f"{self.width}x{self.height}",
                    '-i', '-', # The imput comes from a pipe
                    '-an', # Tells FFMPEG not to expect any audio
                    '-vcodec', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    "-loglevel", "error",
                    f'videos/{filename}_{Renderer.count}.mp4'
                ]
            pipe = sp.Popen(command, stdin=sp.PIPE)
        

        frame_number = 0
        while frame_number <= self.timeline._lifetime:
            print(
                f"creating frame: {frame_number} | completed: {(frame_number / self.timeline._lifetime) * 100:.2f}%",
                end="\r")
            frame = Frame(self.width, self.height)
            self.timeline.exec(frame_number)

            for k, v in pd.json_normalize(g, sep='.').to_dict(orient='records')[0].items():
                if issubclass(type(v), Place):
                    if v not in b.values():
                        frame.add(v)

            svg_data = frame.generate().encode()
            if video:
                convert_svg_2_png = sp.Popen(
                    ['convert', 'svg:-', 'png:-'],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE,
                    # encoding='utf-8'
                )
                png_data, error_message = convert_svg_2_png.communicate(input=svg_data)
                pipe.stdin.write(png_data)
            elif png:
                p = mp.Process(target=self.parallel_svg2png, args=(svg_data, frame_number))
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
                if save_frames.get(-1):
                    frame.save(f'svgs/{Renderer.count}/{str(frame_number).zfill(8)}.svg')
                elif save_frames.get(frame_number, False):
                    frame.save(f'svgs/{Renderer.count}/{frame_number}.svg')

            for element in frame.elements.values():
                element.dynamic_reset()
                try:
                    for element in element.get_mask().elements:
                        element.dynamic_reset()
                except:
                    pass

            frame_number += 1

        if video:
            pipe.stdin.close()
            pipe.wait()
            pipe.terminate()

    def parallel_svg2png(self, svg_data, frame_number):
        convert_svg_2_png = sp.Popen(
            ['convert', 'svg:-', 'png:-'],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            # encoding='utf-8'
        )
        
        png_data, error_message = convert_svg_2_png.communicate(input=svg_data)

        with open(f'pngs/{Renderer.count}/{str(frame_number).zfill(8)}.png', 'wb') as f:
            f.write(png_data)



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
