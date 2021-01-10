# coding: utf-8
print("Loading...")

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
            write('新视频输入路径: {}'.format(video_in_path))

def image_in_cb():
    global image_in_path
    x = filedialog.askopenfilename(filetypes=(('image files', '*.jpg;*.jpeg;*.png'),))
    if x is not None:
        if len(x) > 0:
            image_in_path = x
            write('新图像输入路径: {}'.format(image_in_path))

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
    q.put('本节包含开发人员修复此问题所需的详细信息。')
    q.put('如果您要报告错误，请包括整个部分。')
    q.put('如果您忽略了其中任何一个，开发人员很有可能将无法提供帮助。')
    q.put('错误: 接收到了 {} 在阶段 "{}".'.format(type_.__name__, stage))
    q.put('信息: "{}"'.format(str(value)))
    q.put('完整的异常信息:')
    for s in traceback.format_tb(tb):
        q.put(s)
    q.put('<log>')
    q.put(aux)
    q.put('</log>')
    q.put('<inputs>')
    q.put(inputs)
    q.put('</inputs>')
    q.put('这是崩溃报告部分的最后一行。')
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
                q.put('重新加载存档点...')
                checkpoints['cpu'] = cpu
                reload()
                q.put('重新加载存档点完成')
            if os.path.isfile('tmp.mp4'):
                os.remove('tmp.mp4')
            q.put('加载资源...')
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
            q.put('资源已载入')
            for frame in make_animation_modified(img0, iter(vid0), checkpoints['g'], checkpoints['kp'], cpu=cpu, relative=relative):
                vid1.append_data(img_as_ubyte(resize(frame, size)))
                progress += 1
            print('正在将输入写入文件...')
            vid1.close()
            q.put('正在整合音频到输出文件...')
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
        q.put('ffmpeg崩溃了!')
        q.put('通常，这意味着深度伪造进程有效，但是重新编码失败。')
        shutil.copy('tmp.mp4', vid1n)
        q.put('您可以尝试通过手动重新混合音频流来挽救进度.')
        q.put('如果您输入的视频不包含音频，也会发生这种情况； 如果是这种情况，该文件至少应保持完整。')
        raise e
    except Exception as e:
        msg = 'cpu={}'.format(cpu)
        trace('predict', [vid0n, img0n, vid1n], aux=msg)
        q.put('yanderify崩溃了!')
        q.put('一些常规问题:')
        q.put('- 你有一张AMD显卡. AMD卡因为一些技术原因不在GPU模式中被支持。然而, 你可以用CPU模式运行,尽管会慢.请阅读在顶部关于CPU的说明!')
        q.put('- 你有一张Nvidia的显卡, 不过没有足够的内存或者型号太老了. 新于或等于700-系卡 和大于等于2GB专用显示内存可以正常工作')
        q.put('- 你又可以正常工作的卡, 但没有足够的空闲的显存来运行深度伪造. 浏览器经常导致显存问题. 如果你有任何打开的游戏,关掉他们.')
        q.put('- 有个开发者日了狗了. 如果是这样, 确保提交完整的崩溃日志 (你可能得向上滑!), 除此之外我们帮不了你!')
        raise e
    except KeyboardInterrupt as e:
        q.put('正在停止...')
    else:
        q.put('成功!')
    finally:
        stopped = True

def start():
    global stopped
    if not stopped:
        stopped = True
        return
    write('启动中...')
    if (video_in_path is None) or (image_in_path is None) or (video_out_path is None):
        write('错误: 必须选择文件')
        return
    if run_lock.locked():
        write('错误: 已经启动了!')
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
        c = Checkbutton(master, text='我没有 >=GTX750 的NVIDIA显卡', variable=use_cpu)
        c.grid(row=0, column=0)
        video_in = Button(master, text='选择视频', command=video_in_cb)
        video_in.grid(row=0, column=1)
        image_in = Button(master, text='选择图片', command=image_in_cb)
        image_in.grid(row=0, column=2)
        video_out = Button(master, text='选择输出位置', command=video_out_cb)
        video_out.grid(row=0, column=3)
        kitty_button = Button(master, text='无限猫图', command=show_kitty)
        kitty_button.grid(row=0, column=4)
        self.go = Button(master, text='开始', command=start)
        self.go.grid(row=1, column=4)
        self.progress_bar = Progressbar(master, orient=HORIZONTAL, mode='determinate', length=500)
        self.progress_bar.grid(row=1, column=0, columnspan=4)
        st = scrolledtext.ScrolledText(master, state=DISABLED)
        st.grid(row=2, column=0, columnspan=5, rowspan=7)
        write('启动了Yanderify 3.0.6-alpha测试版-0')
        write('警告: 这不是一个稳定版，不应该这样用.')
        write('说明: CPU模式在地段电脑或大多数笔记本上通常会导致系统锁定.')
        write('如果您通过拒绝听取此建议而电脑被锁定，我们将不承担任何责任。')
        write('dunnousername#8672写的.')
        write('深受 windy 的启发')
        adv_toggle = Button(master, text='切换高级选项', command=adv_toggle_cmd)
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
        self.go['text'] = '开始' if stopped else '停止'
        try:
            while True:
                msg = q.get(block=False)
                write(msg)
        except queue.Empty:
            self.after(50, self.process_queue)

h_helper.finish()

app = Yanderify(master=root)
app.mainloop()
