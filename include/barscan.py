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


def get_pic(url=None, ip=None):

    url = url or get_url(ip)

    try:
        imgResp = urllib.request.urlopen(url)
        imgNp = np.asarray(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp,-1)
        return img

    except Exception as e:
        raise e


def test_url(url):
    try:
        get_pic(url)
        return True
    except urllib.request.URLError:
        return False

def get_url(ip):
    return 'http://{}/shot.jpg'.format(ip)


def test_ip(ip):
    return test_url(get_url(ip))



def ask_url(ip=None):

    success = False

    while not success:
        ip = ip = input("Input camera IP: >")
        url = get_url(ip)

        if ip in ['q', 'x']:
            raise KeyboardInterrupt

        success = test_url(url)
        print('Invalid IP. Please retry')
        ip = None

    print('Camera status: online')

    return url


def get_barcode(img):
    barcodes = pyzbar.decode(img)
    output = [str(int(el.data)) for el in barcodes]

    return output


def ip2barcode(ip):
    return get_barcode(get_pic(ip=ip))


if __name__ == '__main__':
    img = shootpic(ip=MAIN_IP)
    barcode = get_barcode(img)
