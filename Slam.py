from roboflowoak import RoboflowOak
import cv2
import time
import numpy as np

if __name__ == '__main__':
    # instantiating an object (rf) with the RoboflowOak module
    rf = RoboflowOak(model="obstacle-detection-f3yxc",
    api_key="mN2NdBpq63DRwJ0uy5ml", rgb=True, depth=True,
    device=, device_name="19443010F18EDB1200", blocking=True)
    while True:
        t0 = time.time()
        result, frame, raw_frame, depth = rf.detect()    
        predictions = result["predictions"]
        #{
        #    predictions:
        #    [ {
        #        x: (middle),
        #        y:(middle),
        #        width: ,
        #        height: ,
        #        depth: ###->,
        #        confidence: ,
        #        class: ,
        #        mask: { }
        #       }
        #    ]
        #}
        #frame - frame after preprocs, with predictions
        #raw_frame - original frame from your OAK
        #depth - depth map for raw_frame, center-rectified
        # to the center camera 
        # To access specific values within "predictions" use:
        # p.json()[a] for p in predictions
        # set "a" to the index you are attempting to access
        # Example: accessing the "y"-value:
        # p.json()['y'] for p in predictions
        
        t = time.time()-t0
        print("INFERENCE TIME IN MS ", 1/t)
        print("PREDICTIONS ", [p.json() for p in predictions])
        
        # setting parameters for depth calculation
        max_depth = np.amax(depth)
        cv2.imshow("depth", depth/max_depth)
        # displaying the video feed as successive frames      
        cv2.imshow("frame", frame)
        
        # how to close the OAK inference window/stop inference:
        # CTRL+q or CTRL+c
        if cv2.waitKey(1) == ord('q'):
            break

