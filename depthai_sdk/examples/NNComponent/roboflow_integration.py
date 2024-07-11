# from depthai_sdk import OakCamera
# import depthai_sdk
# # Download & deploy a model from Roboflow universe:
# # # https://universe.roboflow.com/david-lee-d0rhs/american-sign-language-letters/dataset/6


# with OakCamera() as oak:
#     color = oak.create_camera('color',fps=30, encode='h264')
#     model_config = {
#         'source': 'roboflow',
#         'model': 'obstacle-detection-f3yxc/1',
#         'key': 'mN2NdBpq63DRwJ0uy5ml'
#     }
#     nn = oak.create_nn(model_config, color)
#     oak.visualize(nn)
#     oak.start(blocking=True)

# from depthai_sdk import OakCamera

# with OakCamera() as oak:
#     color = oak.create_camera('color')
#     model_config = {
#         'source': 'roboflow',
#         'model': 'obstacle-detection-f3yxc/1',
#         'key': 'mN2NdBpq63DRwJ0uy5ml'
#     }
#     nn = oak.create_nn(model_config, color)
#     oak.visualize([nn.out.main, nn.out.spatials], fps=True)
#     oak.start(blocking=True)

# from depthai_sdk import OakCamera

# # Download & deploy a model from Roboflow universe:
# # # https://universe.roboflow.com/david-lee-d0rhs/american-sign-language-letters/dataset/6

# with OakCamera() as oak:
#     color = oak.create_camera('color')
#     model_config = {
#         'source': 'roboflow',
#         'model': 'obstacle-detection-f3yxc/1',
#         'key': 'mN2NdBpq63DRwJ0uy5ml'
#     }
#     nn = oak.create_nn(model_config, color)
#     oak.visualize(nn, fps=True)
#     oak.start(blocking=True)


from depthai_sdk import OakCamera

with OakCamera() as oak:
    # Set up the camera and the Roboflow model
    color_cam = oak.create_camera('color', resolution='1080p')
    model_config = {
        'source': 'roboflow',
        'model': 'obstacle-detection-f3yxc/1',
        'key': 'mN2NdBpq63DRwJ0uy5ml'
    }
    nn = oak.create_nn(model_config, color_cam)
    nn.config_nn(resize_mode='letterbox')

    # Set up the output queues for the disparity map and other options
    depth_queue = oak.create_imu(name="depth", max_size=4, max_data_size=640 * 400 * 2)
    spatial_queue = oak.create_imu(name="spatial", max_size=4, max_data_size=nn.get_spatial_out_size())

    # Visualize the outputs and start the pipeline
    visualizer = oak.visualize([nn, nn.out.passthrough, nn.out.depth, nn.out.spatials], fps=True)
    oak.start(pipeline=nn, output_queues=[depth_queue, spatial_queue], blocking=True)
