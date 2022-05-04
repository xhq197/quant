file_path = 'C:\Users\JiangHR\Desktop\2020数学建模\高速公路视频截图\';
savepath='C:\Users\JiangHR\Desktop\2020数学建模\处理图像';

x = 1:100;
disp(x)
for i=1:100
    Image=imread([savepath,num2str(i,'%04d'),'.png']);    %读入图片，如1_predict_prob.png
    aera = bwarea(Image);
    aeras(i) = aera/88;
end

plot(x, aeras)