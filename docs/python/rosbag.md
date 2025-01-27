可以用python处理.bag文件，不用安装ros系统。

```
conda create -n rosbag python==3.7.6 -y
conda install -c conda-forge ros-roslz4 -y
pip install --extra-index-url https://rospypi.github.io/simple/ rospy rosbag
conda install -c conda-forge pillow opencv -y
```

使用例:
```
import rosbag
import sys
from PIL import Image
import os
import numpy as np
import cv2


if __name__ == '__main__':
    bag_dir = sys.argv[1]
    img_dir = os.path.join(bag_dir, 'image2')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    bag_file = os.path.join(bag_dir, 'shopping_street_1_seq1.bag')
    bag = rosbag.Bag(bag_file)
    index = 0
    imgname = os.path.join(img_dir, '{:0>5d}.jpg')
    for topic, msg, t in bag.read_messages(topics='/cam0/image_raw'):
        header = msg.header
        header_seq = header.seq 
        stamp_sec = header.stamp.secs
        stamp_nsec = header.stamp.nsecs
        data = msg.data #bytes
        img = np.frombuffer(data, dtype=np.uint8) #转化为numpy数组
        img = img.reshape(msg.height, msg.width)
        cv2.imwrite(imgname.format(index), img) #保存为图片
        print('{:0>5d} {} {} {}'.format(index, header_seq, stamp_sec, stamp_nsec))
        index += 1
        

```
