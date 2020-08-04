# coding: utf-8
print('Installation is almost done! doing some sanity checks')
try:
    import numpy as np
    a = np.zeros((2, 2))
    import subprocess
    subprocess.check_output('ffmpeg -h')
except Exception as e:
    print('Failed a sanity check. You should tell the devs about this!')
    raise e
print('Installation done!')