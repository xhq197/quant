import numpy as np
import matplotlib.pyplot as plt
import math

img = plt.imread('.\\cameraman.jpg')
#生成高斯滤波器
sum = 0
sigma = 2
gaussian = np.zeros([5,5])
for i in range(5):
    for j in range(5):
        gaussian[i,j] = math.exp(-1/2*(np.square(i-3)*np.square(j-3)/(sigma**2)))/np.sqrt(2*math.pi*sigma**2)
        sum +=  gaussian[i,j]

gaussian = gaussian / sum
#print(gaussian)

#对图片进行高斯滤波
img_gray = np.dot(img[...,:3], [0.299, 0.587, 0.114])
W, H = img.shape
new_img = np.zeros([W-4, H-4])
for i in range(W-4):
    for j in range(H-4):
        new_img[i,j] = np.sum(img[i:i+5, j:j+5]*gaussian)


plt.figure()
plt.imshow(new_img, cmap='gray')



#计算梯度
W1, H1 = new_img.shape

prewitty = np.array([
    [-1,-1,-1],
    [0,0,0],
    [1,1,1]
    ])
prewittx = prewitty.T

sobely = np.array([
    [-1,-2,-1],
    [0,0,0],
    [1,2,1]
    ])
sobelx = sobely.T

dx = np.zeros([W1-2, H1-2])
dy = np.zeros([W1-2, H1-2])
d = np.zeros([W1-2, H1-2])
for i in range(W1-2):
    for j in range(H1-2):
            dx[i, j] = np.sum(new_img[i:i+3, j:j+3]*sobelx)
            dy[i, j] = np.sum(new_img[i:i+3, j:j+3]*sobely)
            d[i, j] = np.sqrt(np.square(dx[i, j]) + np.square(dy[i, j]))
plt.figure()
plt.imshow(d, cmap='gray')



#非极大值抑制
W2, H2 = d.shape
NMS = np.zeros([W2, H2])

for i in range(1, W2-1):
    for j in range(1, H2-1):
        if d[i, j] == 0:
            NMS[i, j] = 0
        else:
            g_x = dx[i, j]
            g_y = dy[i, j]
            g0 = d[i, j]
            if np.abs(g_y) < np.abs(g_x):
                w = np.abs(g_y) / np.abs(g_x)
                p2 = d[i, j-1]
                p4 = d[i, j+1]
                if g_x * g_y > 0:
                    p1 = d[i+1, j-1]
                    p3 = d[i-1, j+1]
                else:
                    p1 = d[i-1, j-1]
                    p3 = d[i+1, j+1]
            else:
                w = np.abs(g_x) / np.abs(g_y)
                p2 = d[i-1, j]
                p4 = d[i+1, j]
                if g_x * g_y > 0:
                    p1 = d[i-1, j-1]
                    p3 = d[i+1, j+1]
                else:
                    p1 = d[i-1, j+1]
                    p3 = d[i+1, j-1]

            g1 = w * p1 + (1 - w) * p2
            g2 = w * p3 + (1 - w) * p4
            if g0 >= g1 and g0 >= g2:
                NMS[i, j] = g0
            else:
                NMS[i, j] = 0

plt.figure()
plt.imshow(NMS, cmap='gray')

#双阈值法
W3, H3 = NMS.shape
F = np.zeros([W3,H3])
LP = 0.1 * np.max(NMS)
HP = 0.2 * np.max(NMS)
for i in range(1, W3-1):
    for j in range(1,H3-1):
        if (NMS[i,j] >= HP):
            F[i,j] = 1
        elif (NMS[i,j] < LP):
            F[i,j] = 0
        elif ((NMS[i-1,j-1:j+2]>=HP).any() or (NMS[i+1,j-1:j+2]>=HP).any() or (NMS[i,[j-1,j+1]]>=HP).any()):
            F[i,j] = 1

plt.figure()
plt.imshow(F, cmap='gray')
plt.show()



