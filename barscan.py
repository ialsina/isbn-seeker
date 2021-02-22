import cv2
import urllib.request
import numpy as np
import time
from pyzbar import pyzbar

MAIN_IP = '[MAIN_IP HERE]'

def shootpic(url=None, ip=None):

    url = url or get_url(ip)
    
    while True:
        # Use urllib to get the image and convert into a cv2 usable format
            imgResp=urllib.request.urlopen(url)
            imgNp=np.asarray(bytearray(imgResp.read()),dtype=np.uint8)
            img=cv2.imdecode(imgNp,-1)
        
            # put the image on screen
            cv2.namedWindow('IPWebcam', cv2.WINDOW_NORMAL)
            cv2.imshow('IPWebcam',img)
            cv2.resizeWindow('IPWebcam', 600, 600)
        
            #To give the processor some less stress
            time.sleep(0.1) 
        
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break

    cv2.destroyAllWindows()
    
    return img

def get_url(ip=None):
    ip = ip or input("Input camera IP: >")
    return 'http://{}/shot.jpg'.format(ip)


def get_barcode(img):
    barcodes = pyzbar.decode(img)
    output = [el.data for el in barcodes]

    if len(output) == 0:
        return None
    elif len(output) == 1:
        return output[0]
    else:
        return output


if __name__ == '__main__':
    img = shootpic(ip=MAIN_IP)
    barcode = get_barcode(img)