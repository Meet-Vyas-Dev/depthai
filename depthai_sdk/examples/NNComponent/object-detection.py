from depthai_sdk import OakCamera



with OakCamera() as oak:
    color = oak.create_camera('color', resolution='1080p')

    nn = oak.create_nn('obstacle_detection', color)
    nn.config_nn(resize_mode='letterbox')

    visualizer = oak.visualize([nn, nn.out.passthrough], fps=True)
    oak.start(blocking=True)

with OakCamera() as oak:
    color = oak.create_camera('color')
    model_config = {
        'source': 'roboflow',
        'model': 'obstacle-detection-f3yxc/1',
        'key': 'mN2NdBpq63DRwJ0uy5ml'
    }
    nn = oak.create_nn(model_config, color)
    oak.visualize([nn.out.main, nn.out.spatials], fps=True)
    oak.start(blocking=True)