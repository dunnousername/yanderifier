# coding: utf-8

import locale
sys_language = locale.getdefaultlocale()
if "zh" in sys_language[0]:
    sys_language = "chinese"
else:
    sys_language = "english"
import json
with open("languages.json", "r", encoding="utf-8") as f:
    languages = json.load(f)

print(languages["loading"][sys_language])

import hhelper
import warnings
import sys

if 'debug' not in sys.argv:
    warnings.simplefilter('ignore')

h_helper = hhelper.HHelper()
h_helper.forward(0.5)

progress = 0
progress_max = 0
stopped = True

try:
    from steghelper import ffmpeg_flags
except ImportError:
    ffmpeg_flags = False

h_helper.forward(1.5)

import matplotlib
matplotlib.use('Agg')
from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter.ttk import *
import os
import queue
import shlex
import shutil
import subprocess
import threading
import traceback

h_helper.forward(3.5)
import imageio
import torch
from skimage import img_as_ubyte, img_as_float
import skimage.transform as transform
import cv2
import numpy as np
import webbrowser
from demo import *

# written by dunnousername#8672

#print('Loading checkpoints...')

h_helper.forward(5.5)

checkpoints = {
    'cpu': False
}

def reload():
    with warnings.catch_warnings():
        global checkpoints
        warnings.simplefilter('ignore')
        demo_g, demo_kp = load_checkpoints('../fomm/config/vox-256.yaml', 'checkpoint.tar', cpu=checkpoints['cpu'])
        checkpoints['g'] = demo_g
        checkpoints['kp'] = demo_kp

reload()

h_helper.forward(8.5)
#print('Initializing windows...')

root = Tk()
use_cpu = IntVar()
st = None
video_in_path = None
image_in_path = None
video_out_path = None
q = queue.Queue()

run_lock = threading.Lock()

def write_noln(text):
    st.configure(state='normal')
    st.insert(END, text)
    st.configure(state='disabled')
    st.yview(END)

def write_ln():
    write_noln('\n')

def write(text):
    write_noln(text)
    write_ln()

def video_in_cb():
    global video_in_path
    x = filedialog.askopenfilename(filetypes=(('video files', '*.mp4;*.mkv;*.mov;*.avi'),))
    if x is not None:
        if len(x) > 0:
            video_in_path = x
            write(languages["new_video_input_path"][sys_language].format(video_in_path))

def image_in_cb():
    global image_in_path
    x = filedialog.askopenfilename(filetypes=(('image files', '*.jpg;*.jpeg;*.png'),))
    if x is not None:
        if len(x) > 0:
            image_in_path = x
            write(languages["new_image_input_path"][sys_language].format(image_in_path))

def video_out_cb():
    global video_out_path
    x = filedialog.asksaveasfilename(filetypes=(('.mp4 files', '*.mp4'),))
    if x is not None:
        if len(x) > 0:
            if not x.endswith('.mp4'):
                x = x + '.mp4'
            video_out_path = x
            write('新视频输出路径: {}'.format(video_out_path))

def trace(stage, inputs, aux=None):
    sep = '==========================='
    (type_, value, tb) = sys.exc_info()
    q.put(sep)
    q.put(languages["err_msg_1"][sys_language])
    q.put(languages["err_msg_2"][sys_language])
    q.put(languages["err_msg_3"][sys_language])
    q.put(languages["err_msg_4"][sys_language].format(type_.__name__, stage))
    q.put(languages["err_msg_5"][sys_language].format(str(value)))
    q.put(languages["err_msg_6"][sys_language])
    for s in traceback.format_tb(tb):
        q.put(s)
    q.put('<log>')
    q.put(aux)
    q.put('</log>')
    q.put('<inputs>')
    q.put(inputs)
    q.put('</inputs>')
    q.put(languages["err_msg_7"][sys_language])
    q.put(sep)

def acceptable_resolution(x, y):
    modulus = 16
    if not (x % modulus == 0):
        x = modulus * (x // modulus + 1)
    if not (y % modulus == 0):
        y = modulus * (y // modulus + 1)
    return x, y

relative = BooleanVar()
relative.set(True)

# this function is from https://github.com/AliaksandrSiarohin/first-order-model/blob/master/demo.py and is slightly modified
def make_animation_modified(source_image, driving_generator, generator, kp_detector, relative=True, adapt_movement_scale=True, cpu=False):
    with torch.no_grad():
        source = torch.tensor(source_image[np.newaxis].astype(np.float32)).permute(0, 3, 1, 2)
        if not cpu:
            source = source.cuda()
        
        first = next(driving_generator)
        driving = torch.tensor(np.array(first)[np.newaxis][np.newaxis].astype(np.float32)).permute(0, 4, 1, 2, 3)
        kp_source = kp_detector(source)
        kp_driving_initial = kp_detector(driving[:, :, 0])

        def process(frame):
            driving_frame = torch.tensor(np.array(frame)[np.newaxis][np.newaxis].astype(np.float32)).permute(0, 4, 1, 2, 3)[:, :, 0]
            if not cpu:
                driving_frame = driving_frame.cuda()
            kp_driving = kp_detector(driving_frame)
            kp_norm = normalize_kp(kp_source=kp_source, kp_driving=kp_driving,
                                   kp_driving_initial=kp_driving_initial, use_relative_movement=relative,
                                   use_relative_jacobian=relative, adapt_movement_scale=adapt_movement_scale)
            out = generator(source, kp_source=kp_source, kp_driving=kp_norm)
            del driving_frame
            del kp_driving
            del kp_norm
            result = np.transpose(out['prediction'].data.cpu().numpy(), [0, 2, 3, 1])[0]
            del out
            return result

        yield process(first)
        for frame in driving_generator:
            yield process(frame)

def resize(img, shape):
    return transform.resize(img, shape, anti_aliasing=True)

def worker_thread(vid0n, img0n, vid1n, cpu, relative):
    try:
        global progress
        global progress_max
        global stopped
        global checkpoints
        with run_lock:
            if not (cpu == checkpoints['cpu']):
                q.put(languages["reloading_checkpoints"][sys_language])
                checkpoints['cpu'] = cpu
                reload()
                q.put(languages["finished_loading_checkpoints"][sys_language])
            if os.path.isfile('tmp.mp4'):
                os.remove('tmp.mp4')
            q.put(languages["loading_sources"][sys_language])
            vid0r = imageio.get_reader(vid0n)
            fps = vid0r.get_meta_data()['fps']
            vid0 = []
            while True:
                try:
                    im = vid0r.get_next_data()
                except (IndexError, imageio.core.CannotReadFrameError):
                    break
                else:
                    vid0.append(resize(im, (256, 256))[..., :3])
            progress = 0
            progress_max = len(vid0)
            img0 = imageio.imread(img0n)
            # TODO: v is this line really neccessary? v
            #img0 = cv2.cvtColor(img0, cv2.COLOR_BGR2RGB)
            size = img0.shape[:2][::-1]
            size = acceptable_resolution(size[0], size[1])
            img0 = resize(img0, (256, 256))[..., :3]
            vid1 = imageio.get_writer('tmp.mp4', fps=fps)
            q.put(languages["sources_loaded"][sys_language])
            for frame in make_animation_modified(img0, iter(vid0), checkpoints['g'], checkpoints['kp'], cpu=cpu, relative=relative):
                vid1.append_data(img_as_ubyte(resize(frame, size)))
                progress += 1
            print(languages["writing_output_to_file"][sys_language])
            vid1.close()
            q.put(languages["muxing_audio_streams_into_output_file"][sys_language])
            cmd = shlex.split('ffmpeg -y -hide_banner -loglevel warning -i tmp.mp4 -i')
            cmd.append(vid0n)
            cmd.extend(shlex.split('-map 0:v -map 1:a -movflags faststart -c:v libx264 -pix_fmt yuv420p -x264-params "nal-hrd=cbr" -b:v 1200K -minrate 1200K -maxrate 1200K -bufsize 2M'))
            if ffmpeg_flags:
                cmd.extend(ffmpeg_flags)
            cmd.append(vid1n)
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            q.put(output)
            #os.remove('tmp.mp4')
    except subprocess.CalledProcessError as e:
        msg = 'command "{}" returned non-zero error code {}: {}'.format(
            e.cmd,
            e.returncode,
            e.output
        )
        trace('ffmpeg', [vid0n, img0n, vid1n], aux=msg)
        q.put(languages["suberr1"][sys_language])
        q.put(languages["suberr2"][sys_language])
        shutil.copy('tmp.mp4', vid1n)
        q.put(languages["suberr3"][sys_language])
        q.put(languages["suberr4"][sys_language])
        raise e
    except Exception as e:
        msg = 'cpu={}'.format(cpu)
        trace('predict', [vid0n, img0n, vid1n], aux=msg)
        q.put(languages["othererr1"][sys_language])
        q.put(languages["othererr2"][sys_language])
        q.put(languages["othererr3"][sys_language])
        q.put(languages["othererr4"][sys_language])
        q.put(languages["othererr5"][sys_language])
        q.put(languages["othererr6"][sys_language])
        raise e
    except KeyboardInterrupt as e:
        q.put(languages["keyboardinterrupt"][sys_language])
    else:
        q.put(languages["success"][sys_language])
    finally:
        stopped = True

def start():
    global stopped
    if not stopped:
        stopped = True
        return
    write(languages["start1"][sys_language])
    if (video_in_path is None) or (image_in_path is None) or (video_out_path is None):
        write(languages["start2"][sys_language])
        return
    if run_lock.locked():
        write(languages["start3"][sys_language])
        return
    stopped = False
    threading.Thread(target=worker_thread, args=(video_in_path, image_in_path, video_out_path, use_cpu.get(), relative.get())).start()

def show_kitty():
    webbrowser.open('https://thiscatdoesnotexist.com/')

adv_panel_shown = False
toggle_adv_panel = False

def adv_toggle_cmd():
    global toggle_adv_panel
    toggle_adv_panel = True

class Yanderify(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.after(50, self.process_queue)

    def create_widgets(self):
        global st
        master = self.master
        c = Checkbutton(master, text=languages["class1"][sys_language], variable=use_cpu)
        c.grid(row=0, column=0)
        video_in = Button(master, text=languages["class2"][sys_language], command=video_in_cb)
        video_in.grid(row=0, column=1)
        image_in = Button(master, text=languages["class3"][sys_language], command=image_in_cb)
        image_in.grid(row=0, column=2)
        video_out = Button(master, text=languages["class4"][sys_language], command=video_out_cb)
        video_out.grid(row=0, column=3)
        kitty_button = Button(master, text=languages["class5"][sys_language], command=show_kitty)
        kitty_button.grid(row=0, column=4)
        self.go = Button(master, text=languages["class6"][sys_language], command=start)
        self.go.grid(row=1, column=4)
        self.progress_bar = Progressbar(master, orient=HORIZONTAL, mode='determinate', length=500)
        self.progress_bar.grid(row=1, column=0, columnspan=4)
        st = scrolledtext.ScrolledText(master, state=DISABLED)
        st.grid(row=2, column=0, columnspan=5, rowspan=7)
        write(languages["class7"][sys_language])
        write(languages["class8"][sys_language])
        write(languages["class9"][sys_language])
        write(languages["class10"][sys_language])
        write(languages["class11"][sys_language])
        write(languages["class12"][sys_language])
        adv_toggle = Button(master, text=languages["class13"][sys_language], command=adv_toggle_cmd)
        adv_toggle.grid(row=9, column=0, columnspan=5)
        self.adv_panel = Frame(master)
        adv_relative = Checkbutton(self.adv_panel, text='Relative', variable=relative)
        adv_relative.grid(row=0, column=0)

    def process_queue(self):
        global toggle_adv_panel
        global adv_panel_shown
        if toggle_adv_panel:
            toggle_adv_panel = False
            adv_panel_shown = not adv_panel_shown
            if adv_panel_shown:
                self.adv_panel.grid(row=10, column=0, rowspan=3, columnspan=5)
            else:
                self.adv_panel.grid_remove()
        self.progress_bar['value'] = 100 * min(1.0, progress / max(progress_max, 1.0))
        self.go['text'] = languages["class14"][sys_language] if stopped else languages["class15"][sys_language]
        try:
            while True:
                msg = q.get(block=False)
                write(msg)
        except queue.Empty:
            self.after(50, self.process_queue)

h_helper.finish()

app = Yanderify(master=root)
app.mainloop()
