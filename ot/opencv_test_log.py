with open("opencv_test_results.txt", "w", encoding="utf-8") as f:
    try:
        import cv2
        f.write("OpenCV successfully loaded!\n")
        f.write(f"OpenCV version: {cv2.__version__}\n")
    except ImportError as e:
        f.write(f"OpenCV could not be loaded: {e}\n")

    try:
        import numpy as np
        f.write("NumPy successfully loaded!\n")
    except ImportError as e:
        f.write(f"NumPy could not be loaded: {e}\n")

    try:    
        from PIL import Image
        f.write("Pillow successfully loaded!\n")
    except ImportError as e:
        f.write(f"Pillow could not be loaded: {e}\n") 