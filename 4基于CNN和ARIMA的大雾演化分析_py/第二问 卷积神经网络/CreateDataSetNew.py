import  numpy as np
import  os
import cv2 as cv

file_name = 'train6'
rootpath = f'./{file_name}/'
list = os.listdir(rootpath) #列出文件夹下所有的目录与文件
#设定图像宽高
imgwidth = 220
imgheight = 220

imgdata = []
imgtag = []
a = list.copy()
b = [int(x) for x in a]



b.sort()
list = [str(x) for x in b]
print('########list:\n',list)
for i in range(len(list)):
    #对于子目录进行处理
    # print(i)
    currentpath = rootpath+list[i]
    currentlist = os.listdir(currentpath)
    print(list[i])
    for j in range(len(currentlist)):
        #图像位置
        imgpath = currentpath + "/" + currentlist[j]
        #有后缀为db的文件
        if currentlist[j][-3:] == "jpg":
            #i为类目
            imgtag.append(i)
            #加载图像
            img = cv.imread(imgpath,0)
            img = cv.resize(img,(imgwidth,imgheight))
            # #将图像标准化，尝试解决输出结果相同的问题
            img = (img - img.mean()) / (img.std() + 1e-8)
            print(img.shape)
            imgdata.append(img)
    print('#######\n',list[i], '--', i)



imgtag = np.array(imgtag)
imgdata = np.array(imgdata)
imgtag = imgtag.reshape(imgtag.shape[0],1)
#增加一维灰度维
imgdata = imgdata.reshape(imgdata.shape[0],imgdata.shape[1],imgdata.shape[2],1)
print(imgdata.shape,imgtag.shape)
#存储
np.save(f"./x_{file_name}.npy",imgdata)
np.save(f"./y_{file_name}.npy",imgtag)
print(len(list))