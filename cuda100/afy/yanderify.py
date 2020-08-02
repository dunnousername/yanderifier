# coding: utf-8
print("If you are reading this, I'm not dead yet.")

from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter.ttk import *
import os
import queue
import shlex
import shutil
import subprocess
import sys
import threading
import traceback
import imageio
import cv2
import webbrowser
from afy.predictor_local import PredictorLocal

# written by dunnousername#86??

root = Tk()
use_cpu = IntVar()
st = None
video_in_path = None
image_in_path = None
video_out_path = None
q = queue.Queue()
stopped = True

progress = 0
progress_max = 0
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
            write('New video input path: {}'.format(video_in_path))

def image_in_cb():
    global image_in_path
    x = filedialog.askopenfilename(filetypes=(('image files', '*.jpg;*.jpeg;*.png'),))
    if x is not None:
        if len(x) > 0:
            image_in_path = x
            write('New image input path: {}'.format(image_in_path))

def video_out_cb():
    global video_out_path
    x = filedialog.asksaveasfilename(filetypes=(('.mp4 files', '*.mp4'),))
    if x is not None:
        if len(x) > 0:
            if not x.endswith('.mp4'):
                x = x + '.mp4'
            video_out_path = x
            write('New video output path: {}'.format(video_out_path))

def trace(stage, inputs, aux=None):
    sep = '==========================='
    (type_, value, tb) = sys.exc_info()
    q.put(sep)
    q.put('This section contains the details the devs need to fix this issue.')
    q.put('If you are reporting a bug, please include this entire section.')
    q.put('If you leave out any of it, there is a good chance the devs will not be able to help.')
    q.put('Error: received a {} at stage "{}".'.format(type_.__name__, stage))
    q.put('Message: "{}"'.format(str(value)))
    q.put('Full traceback:')
    for s in traceback.format_tb(tb):
        q.put(s)
    q.put('<log>')
    q.put(aux)
    q.put('</log>')
    q.put('<inputs>')
    q.put(inputs)
    q.put('</inputs>')
    q.put('This is the last line of the crash report section.')
    q.put(sep)

def acceptable_resolution(x, y):
    modulus = 16
    if not (x % modulus == 0):
        x = modulus * (x // modulus + 1)
    if not (y % modulus == 0):
        y = modulus * (y // modulus + 1)
    return x, y

def worker_thread(vid0n, img0n, vid1n, device):
    try:
        global progress
        global progress_max
        with run_lock:
            if os.path.isfile('tmp.mp4'):
                os.remove('tmp.mp4')
            q.put('Loading sources...')
            vid0 = imageio.get_reader(vid0n)
            progress = 0
            progress_max = vid0.get_length()
            img0 = imageio.imread(img0n)[:, :, :3]
            # TODO: v is this line really neccessary? v
            #img0 = cv2.cvtColor(img0, cv2.COLOR_BGR2RGB)
            size = img0.shape[:2][::-1]
            size = acceptable_resolution(size[0], size[1])
            img0 = cv2.resize(img0, (256, 256))
            vid1 = imageio.get_writer('tmp.mp4', fps=vid0.get_meta_data()['fps'], mode='I')
            q.put('Sources loaded')
            predictor = PredictorLocal('afy/fomm/config/vox-256.yaml', 'afy/checkpoint.tar', relative=True, adapt_movement_scale=True, device=device)
            predictor.set_source_image(img0)
            q.put('Set source image. Predicting...')
            try:
                for idx, frame in enumerate(vid0):
                    if stopped:
                        q.put('Stopping...')
                        return
                    progress = idx
                    frame = frame[:, :, :3]
                    frame = cv2.resize(frame, (256, 256))
                    prediction = predictor.predict(frame)
                    prediction = cv2.resize(prediction, size)
                    vid1.append_data(prediction)
            except RuntimeError as e:
                q.put(str(e))
            progress = 0
            vid0.close()
            vid1.close()
            q.put('Muxing audio streams into output file...')
            cmd = shlex.split('ffmpeg -y -hide_banner -loglevel warning -i tmp.mp4 -i')
            cmd.append(vid0n)
            cmd.extend(shlex.split('-map 0:v -map 1:a -movflags faststart -c:v libx264 -pix_fmt yuv420p -x264-params "nal-hrd=cbr" -b:v 1200K -minrate 1200K -maxrate 1200K -bufsize 2M'))
            cmd.append(vid1n)
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            q.put(output)
            os.remove('tmp.mp4')
    except subprocess.CalledProcessError as e:
        msg = 'command "{}" returned non-zero error code {}: {}'.format(
            e.cmd,
            e.returncode,
            e.output
        )
        trace('ffmpeg', [vid0n, img0n, vid1n], aux=msg)
        q.put('ffmpeg crashed!')
        q.put('usually this means the deepfake process worked, but re-encoding failed.')
        shutil.copy('tmp.mp4', vid1n)
        q.put('you can attempt to salvage your progress by re-muxing audio streams manually.')
        q.put('this may also happen if your input video contains no audio; if this is the case, the file should be at least mostly intact.')
        raise e
    except Exception as e:
        msg = 'device={}'.format(device)
        trace('predict', [vid0n, img0n, vid1n], aux=msg)
        q.put('yanderify crashed!')
        q.put('some common problems:')
        q.put('- you have an AMD card. AMD cards are not supported in GPU mode for technical reasons. However, you can run in CPU mode, albeit much lower. Please read the disclaimer at the top about CPUs!')
        q.put('- you have an NVIDIA card, but there is either not enough VRAM or the card is too old. >=700-series cards with >=2GB dedicated VRAM should work fine')
        q.put('- you have a working card, but there is not enough available VRAM to run the deepfake process. Browsers commonly cause VRAM issues. If you have any games open, try closing them.')
        q.put('- one of the devs fucked up somewhere. if that is the case, make sure to submit the full crash report (you might have to scroll up!), otherwise we cannot help you!')
        raise e
    else:
        q.put('success!')

def start():
    global stopped
    if not stopped:
        stopped = True
        return
    write('starting...')
    if (video_in_path is None) or (image_in_path is None) or (video_out_path is None):
        write('error: files must be selected')
        return
    if run_lock.locked():
        write('error: already started!')
        return
    stopped = False
    threading.Thread(target=worker_thread, args=(video_in_path, image_in_path, video_out_path, 'cpu' if use_cpu.get() else 'cuda')).start()

def show_kitty():
    webbrowser.open('https://thiscatdoesnotexist.com/')

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
        c = Checkbutton(master, text='Use CPU', variable=use_cpu)
        c.grid(row=0, column=0)
        video_in = Button(master, text='Select Video', command=video_in_cb)
        video_in.grid(row=0, column=1)
        image_in = Button(master, text='Select Image', command=image_in_cb)
        image_in.grid(row=0, column=2)
        video_out = Button(master, text='Select Output', command=video_out_cb)
        video_out.grid(row=0, column=3)
        kitty_button = Button(master, text='∞ kitties', command=show_kitty)
        kitty_button.grid(row=0, column=4)
        self.go = Button(master, text='Go', command=start)
        self.go.grid(row=1, column=4)
        self.progress_bar = Progressbar(master, orient=HORIZONTAL, mode='determinate', length=500)
        self.progress_bar.grid(row=1, column=0, columnspan=4)
        st = scrolledtext.ScrolledText(master, state=DISABLED)
        st.grid(row=2, column=0, columnspan=5, rowspan=7)
        write('Started Yanderify 2.0')
        write('Disclaimer: CPU mode on low-end computers or most laptops generally will cause the system to lock-up.')
        write('We are not liable if you freeze your PC by refusing to listen to this advice.')
        write('Written by dunnousername#86??__Æ¶∬∬rundll32∟err⁉ro▚▒◑◑➽unexpe')
        write('heavily inspired by windy\'s efforts')

    def process_queue(self):
        self.progress_bar['value'] = 100 * min(1.0, progress / max(progress_max, 1.0))
        self.go['text'] = 'Go' if stopped else 'Stop'
        try:
            while True:
                msg = q.get(block=False)
                write(msg)
        except queue.Empty:
            self.after(50, self.process_queue)

app = Yanderify(master=root)
app.mainloop()