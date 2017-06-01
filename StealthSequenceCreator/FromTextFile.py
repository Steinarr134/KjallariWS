with open('SequenceHolder.txt') as f:
    lines = f.readlines()

values = []
bins = []
for line in lines:
    values.append(int("".join(i for i in line.strip().split('\t')[::-1]), base=2))
    bins.append([int(i) for i in line.strip().split("\t")])
print values
# print bins
"1\t0\t1\t1\n"
["1", ]
"1101"

import cv2
import numpy as np


def replace(img, p, c):
    p += 1
    if p == 1:
        img[50:150, 300:400, :] = c
    elif p == 2:
        img[50:150, 100:200, :] = c
    elif p == 3:
        img[200:300, 100:200, :] = c
    elif p == 4:
        img[200:300, 250:350, :] = c
    elif p == 5:
        img[350:450, 250:350, :] = c
    elif p == 6:
        img[350:450, 100:200, :] = c

empty_org = np.zeros((500, 600, 3), np.uint8)
# for i in range(6):
#     replace(empty_org, i, (0, 255, 0))
empty_org[170:180, 100:450, :] = (255, 255, 255)
empty_org[180:470, 440:450, :] = (255, 255, 255)
empty_org[470:480, 100:600, :] = (255, 255, 255)
empty_org[320:330, 0:350, :] = (255, 255, 255)

for i in range(3):
    for binn in bins:
        empty = empty_org.copy()
        for i, b in enumerate(binn):
            if b:
                replace(empty, i, (0, 0, 255))
        cv2.imshow("sdf", empty)
        k = cv2.waitKey(1000)
        if k == 27:
            break
