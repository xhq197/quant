file_path = 'C:\Users\JiangHR\Desktop\2020��ѧ��ģ\���ٹ�·��Ƶ��ͼ\';
savepath='C:\Users\JiangHR\Desktop\2020��ѧ��ģ\����ͼ��';

x = 1:100;
disp(x)
for i=1:100
    Image=imread([savepath,num2str(i,'%04d'),'.png']);    %����ͼƬ����1_predict_prob.png
    aera = bwarea(Image);
    aeras(i) = aera/88;
end

plot(x, aeras)