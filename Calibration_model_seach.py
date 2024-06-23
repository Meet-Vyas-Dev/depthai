from calibrate import Main
from depthai_calibration.calibration_utils import distance
import pathlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors
from scipy.stats import norm
import scipy as sp
import glob
threshold = {"left": 1, "right": 1, "rgb": 1.5}
def plot_reporjection(ax, display_corners, key, all_error):
    center_x, center_y = main.stereo_calib.width[key] / 2, main.stereo_calib.height[key] / 2
    distances = [distance((center_x, center_y), point) for point in np.array(display_corners)]
    max_distance = max(distances)
    circle = plt.Circle((center_x, center_y), max_distance, color='black', fill=True, label = "Calibrated area", alpha = 0.2)
    ax.add_artist(circle)
    ax.set_title(f"Reprojection map camera {key}")
    img = ax.scatter(np.array(display_corners).T[0], np.array(display_corners).T[1], c=all_error, cmap = GnRd, label = "Reprojected", vmin=0, vmax=threshold[key])
    cbar = plt.colorbar(img, ax=ax)
    cbar.set_label("Reprojection error")
    ax.set_xlabel('Width')
    ax.set_xlim([0,main.stereo_calib.width[key]])
    ax.set_ylim([0,main.stereo_calib.height[key]])
    #ax.legend()
    ax.set_ylabel('Height')
    ax.grid()
    return np.mean(all_error)

def plot_histogram(ax, key, error):
    ax.hist(error, range = [0,threshold[key]], bins = 100, edgecolor="Black", density = True)
    xmin, xmax = ax.set_xlim()
    ymin, ymax = ax.set_ylim()
    x = np.linspace(xmin, xmax, len(error))
    mu, std = norm.fit(error)
    p = norm.pdf(x, mu, std)
    
    ax.plot(x, p, 'k', linewidth=2, label = "Fit Gauss: {:.2f} and {:.2f}".format(mu, std))
    param=sp.stats.lognorm.fit(error)
    print(param)
    pdf_fitted = sp.stats.lognorm.pdf(x, param[0], loc=param[1], scale=param[2]) # fitted distribution
    ax.plot(x,pdf_fitted,'r-', label = "Fit Log-Gauss: {:.2f} and {:.2f}".format(param[2], param[0]))
    ax.set_title(key)
    ax.legend()
    ax.set_xlabel("Reprojection error[px]")
    ax.grid()
    return mu, std

def plot_all():
    fig, axes = plt.subplots(nrows=3, ncols=1)
    ax1, ax2, ax3 = axes.flatten()
    ax_ = [ax1, ax2, ax3]
    fig_hist, axes_hist = plt.subplots(nrows=3, ncols=1)
    ax1_h, ax2_h, ax3_h = axes_hist.flatten()
    ax_hist = [ax1_h, ax2_h, ax3_h]
    index = 0
    for key in main.stereo_calib.all_features.keys():
        ax = ax_[index]
        ah = ax_hist[index]
        display_corners = main.stereo_calib.all_features[key]
        all_error = main.stereo_calib.all_errors[key]
        reprojection = plot_reporjection(ax, display_corners, key, all_error)
        mu, std = plot_histogram(ah, key, all_error)
        index += 1

cdict = {'red':  ((0.0, 0.0, 0.0),   # no red at 0
          (0.5, 1.0, 1.0),   # all channels set to 1.0 at 0.5 to create white
          (1.0, 0.8, 0.8)),  # set to 0.8 so its not too bright at 1
'green': ((0.0, 0.8, 0.8),   # set to 0.8 so its not too bright at 0
          (0.5, 1.0, 1.0),   # all channels set to 1.0 at 0.5 to create white
          (1.0, 0.0, 0.0)),  # no green at 1
'blue':  ((0.0, 0.0, 0.0),   # no blue at 0
          (0.5, 1.0, 1.0),   # all channels set to 1.0 at 0.5 to create white
          (1.0, 0.0, 0.0))   # no blue at 1
}


GnRd = colors.LinearSegmentedColormap('GnRd', cdict)
device = "OAK-D-PRO"
save_folder = str(pathlib.Path(__file__).resolve().parent)

static = ['-s', '5.0', '-nx', '29', '-ny', '29', '-ms', '3.7', '-dbg', '-m', 'process', '-brd', device + ".json", "-scp", save_folder]
left_binary = "000000000"
right_binary = "000000000"
color_binary = "000000000"


dynamic = static + ['-pccm', 'left=' + left_binary, 'right=' + right_binary, "rgb=" + color_binary]
main = Main(dynamic)
main.run()

plot_all()
plt.show()


filepath = main.dataset_path
left_path = filepath + '/' + "left"
left_files = glob.glob(left_path + "/*")
left_array = []
right_array = []
for file in left_files:
    if float(file.split("_")[2]) == 0.0 and float(file.split("_")[3]) == 0.0:
        right_array.append(file.replace("left", "right"))
        left_array.append(file)

import depthai as dai
import numpy as np
import cv2
device = dai.Device()
pipeline = dai.Pipeline()


### NEED TO ADD JSON CALIBRATION YOU WANT ###
calib = dai.CalibrationHandler(main.calib_dest_path)
pipeline.setCalibrationData(calib)

left_socket = dai.CameraBoardSocket.LEFT
right_socket = dai.CameraBoardSocket.RIGHT
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
monoLeft.setBoardSocket(left_socket)
monoRight.setBoardSocket(right_socket)
monoLeft.setFps(5)
monoRight.setFps(5)
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_800_P)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_800_P)

xin_left = pipeline.create(dai.node.XLinkIn)
xin_left.setStreamName("left")
xin_right = pipeline.create(dai.node.XLinkIn)
xin_right.setStreamName("right")

xin_left_out = xin_left.out
xin_right_out = xin_right.out

xoutDisparity = pipeline.create(dai.node.XLinkOut)
xoutDisparity.setStreamName("depth")
stereo = pipeline.create(dai.node.StereoDepth)

stereo.initialConfig.setConfidenceThreshold(200)
stereo.initialConfig.setMedianFilter(dai.MedianFilter.MEDIAN_OFF)

xin_left_out.link(stereo.left)
xin_right_out.link(stereo.right)
stereo.disparity.link(xoutDisparity.input)

def send_images(frames):
    input_queues = {"left": device.getInputQueue("left"), "right": device.getInputQueue("right")}
    ts = dai.Clock.now()
    for name, image in dummie_image.items():
        w, h = image.shape[1], image.shape[0]
        frame = cv2.resize(image, (w, h), cv2.INTER_AREA)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if name == "left":
            number = int(1)
            if not rectification:
                frame = cv2.remap(frame, leftMap.map_x, leftMap.map_y, cv2.INTER_LINEAR)
        if name == "right":
            number = int(2)
            if not rectification:
                frame = cv2.remap(frame, rightMap.map_x, rightMap.map_y, cv2.INTER_LINEAR)
        img = dai.ImgFrame()
        img.setData(frame.reshape(h * w))
        img.setTimestamp(ts)
        img.setWidth(w)
        img.setHeight(h)
        img.setInstanceNum(number)
        img.setType(dai.ImgFrame.Type.RAW8)
        input_queues[name].send(img)
rect_display = True
if rect_display:
    xoutRectifiedLeft = pipeline.create(dai.node.XLinkOut)
    xoutRectifiedLeft.setStreamName("rectified_left")
    stereo.rectifiedLeft.link(xoutRectifiedLeft.input)
if rect_display:
    xoutRectifiedRight = pipeline.create(dai.node.XLinkOut)
    xoutRectifiedRight.setStreamName("rectified_right")
    stereo.rectifiedRight.link(xoutRectifiedRight.input)

rectification = True
if not rectification:
    #### Make your own rectification as you wish ###
    meshLeft = None
    meshRight = None
    leftMap = None
    rightMap = None
    stereo.loadMeshData(meshLeft, meshRight)
    stereo.setRectification(False)

output_queues = [xoutDisparity.getStreamName(), "rectified_left", "rectified_right"]

device.startPipeline(pipeline)

### NEED TO ADD IMAGES YOU WANT, HERE IS JUST DUMMY FRAME ###
destroy = False
index = 0
fig, axes = plt.subplots(nrows=3, ncols=2)
ax1, ax2, ax3, ax4, ax5, ax6 = axes.flatten()
_ax_h = ax1, ax3, ax5
_ax_m = ax2, ax4, ax6
while True:
    queues = {name: device.getOutputQueue(name, 4, False) for name in output_queues}
    while True:
        #### LOAD ALL YOUR DUMMY FRAMES AS DICTIONARY ####
        dummie_image = {"left": cv2.imread(left_array[index]), "right": cv2.imread(right_array[index])}
        send_images(dummie_image)
        index += 1
        frames = {name: queue.get().getCvFrame() for name, queue in queues.items()}
        for name, frame in frames.items():
            cv2.imshow(name, frame)
            key = cv2.waitKey(0)
            if name == "depth":
                ax = _ax_h[index-1]
                ax.set_title(left_array[index-1])
                ax.hist(frame.flatten()/100, bins = 100, range=[0.2,1.0], edgecolor = "Black")
                ax.set_xlabel("Distance[m]")
                ax.grid()
                ax_m =_ax_m[index-1]
                image = ax_m.imshow(frame/100, vmin = 0.2, vmax =1.0)
                fig.colorbar(image, label = "Distance [m]", ax=ax_m)
                if index == 3:
                    plt.show()
            if key == ord("q"):
                destroy = True
                break
        if destroy:
            break
    if destroy:
        break