from pathlib import Path

from depthai_sdk import OakCamera
from depthai_sdk.recorders.video_writers.av_writer import AvWriter

fourcc = 'h264' # Can be 'mjpeg', 'h264', or 'hevc'

rec = AvWriter(Path('./'), 'color', fourcc=fourcc)

def save_raw(packet):
    rec.write(packet.msg)

with OakCamera() as oak:
    color = oak.create_camera('color', fps=20)
    encoder = oak.create_encoder(color, codec=fourcc)

    # Stream encoded video packets to host. For visualization, we decode them
    # on the host side, and for callback we write encoded frames directly to disk.
    oak.visualize(encoder, scale=2 / 3, fps=True)
    oak.callback(encoder, callback=save_raw)

    oak.start(blocking=True)

rec.close()
