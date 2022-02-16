import cv2, requests, os
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent

file_name = os.path.join(BASE_DIR, 'Chennai.png')
response = requests.get('https://v3.wttr.in/v3/Chennai.png')
with open(file_name, 'wb') as outfile:
    outfile.write(response.content)

src = cv2.imread(file_name, 1)

fill_color = src[300, 300] #some point in TN

# #replace brown with cyan
# tmp_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
# brown_low=np.array([20,0,0])
# brown_high=np.array([20,255,255])
# mask=cv2.inRange(tmp_hsv,brown_low,brown_high)
# src[mask>0]=(255,255,0)

#replace fill_color with cyan
fill_low=np.array(fill_color)
fill_high=np.array(fill_color)
mask=cv2.inRange(src,fill_low,fill_high)
src[mask>0]=(255,255,0)

cv2.imwrite(file_name, src)


src = cv2.imread(file_name, 1)
src = src[0:0+280, 0:0+612]
#remove black
tmp_grey = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
_,alpha = cv2.threshold(tmp_grey,0,255,cv2.THRESH_BINARY)
b, g, r = cv2.split(src)
rgba = [b,g,r, alpha]
dst = cv2.merge(rgba,4)

cv2.imwrite(file_name, dst)