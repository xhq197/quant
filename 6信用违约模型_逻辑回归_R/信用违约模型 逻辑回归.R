###模型用途：
#根据用户信息、最近60天的交易记录、最近30天APP的使用记录预测评分数据集中各用户的违约概率。

###数据描述
#训练数据集包括用户信息表train.tag、最近60天的交易记录train.trd、
#最近30天APP的使用记录train.beh;评分数据集包括用户信息表pred.tag、最近60天的交易记录pred.trd、
#最近30天APP的使用记录pred.beh。

###预备工作
#在预备工作中已经观察到训练数据集和评分数据集用户id没有重复，
#并且两个数据集中用户信息表中的用户包含其他两个表中的所有用户，并且已经
# 知晓数据集各个特征的数据类型和所包含的数值信息等，详见"数据说明.xlsx"。

###模型思路：
# 1 读取数据并将训练数据集和评分数据集纵向合并。
# 2 从最近60天的交易记录、最近30天APP的使用记录提取特征，并入用户信息表，
# 并且根据特征含义和特征的数据类型做特征分类。
# 3 进一步观察已有特征
# 4 处理数据：根据1、2步所得特征分类和特征进一步的信息做分类处理，主要有：
# 将部分chracter类型的数据z转换成numeric类型，并将所有numeric类型数据中的
# 缺省值用该特征的均值代替；将其他非numeric类型的数据经过one hot处理，最终
# 获得241个特征。
# 5 构建逻辑回归模型，采用向前逐步法进行逻辑回归建模。
# 6 模型评估，使用准确率、ROC曲线、AUC
# 7 对评分数据集进行预测

###模型结论
# 1 在构建模型阶段出现以下警告信息
# Warning message 1:
# glm.fit:算法没有聚合 
# 表明算法不收敛，由于在进行logistic回归时，依照极大似然估计原则进行迭代求解回
# 归系数，glm函数默认的最大迭代次数 maxit=25，当数据不太好时，经过25次迭代可能
# 算法还不收敛，所以可以通过增大迭代次数尝试解决算法不收敛的问题。但是当增大
# 迭代次数后算法仍然不收敛，此时数据就是真的不好了，需要对数据进行奇异值检验等
# 进一步的处理。

# Warning message 2:
# glm.fit:拟合機率算出来是数值零或一
# 表明拟合概率算出来的概率为0或1，可能是由于样本数据是线性可分的，
# 这时logistic回归往往会导致过拟合的问题，因此采用逻辑回归来预测就不太适用
# ，而直接使用规则判断的方法会更简单且适用。
# 2 结果
# maxit=25
# warning 1
# warning 2
# 训练集准确率：训练集准确率：0.7920275 测试集准确率：0.7890123 AUC：0.7030005
# 由评分数据集所得用户违约预测见"result.csv"
# maxit=3000
# warning 2
# 训练集准确率：训练集准确率:0.7262578 测试集准确率：0.7174585 AUC：0.6070061 



######1 原始数据


rm(list=ls())
train.tag=read.csv('C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\训练数据集\\训练数据集\\训练数据集_tag.csv',header=TRUE,stringsAsFactors=F)
train.trd=read.csv('C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\训练数据集\\训练数据集\\训练数据集_trd.csv',header=TRUE,stringsAsFactors=F)
train.beh=read.csv('C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\训练数据集\\训练数据集\\训练数据集_beh.csv',header=TRUE,stringsAsFactors=F)
pred.tag=read.csv('C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\评分数据集b\\b\\评分数据集_tag_b.csv',header=TRUE,stringsAsFactors=F)
pred.trd=read.csv('C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\评分数据集b\\b\\评分数据集_trd_b.csv',header=TRUE,stringsAsFactors=F)
pred.beh=read.csv('C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\评分数据集b\\b\\评分数据集_beh_b.csv',header=TRUE,stringsAsFactors=F)

##1.1 将训练集与测试集合并

if ("flag" %in% colnames(train.tag)){
  train.tag=train.tag[,-c(2)]
}
if ("flag" %in% colnames(train.trd)){
  train.trd=train.trd[,-c(2)]
}
if ("flag" %in% colnames(train.beh)){
  train.beh=train.beh[,-c(2)]
}
tag=rbind(train.tag,pred.tag)
nrow(tag)==43923
trd=rbind(train.trd,pred.trd)
beh=rbind(train.beh,pred.beh)


######2 三表合并


dfm<-tag
#a=b,修改b不影响a

##2.1提取trd的特征

#trd.count:交易次数
fuc.merge=function(dfm,df,col.name){
  df=data.frame(df)
  df$id=rownames(df)
  dfm=merge(dfm,df,by='id',all.x=TRUE)
  #all=TRUE交集 all=FALSE并集 all.x=TRUE左合并 all.y=TRUE右合并 
  colnames(dfm)[ncol(dfm)]=col.name
  return(dfm)
}

trd$count=1
trd.count=tapply(trd$count,factor(trd$id),sum)
dfm=fuc.merge(dfm,trd.count,'trd.count')
dfm[is.na(dfm$trd.count),]$trd.count=0
ncol(dfm)==42+1
nrow(dfm)==43923
#trd.amount:交易金额
trd[trd$Dat_Flg1_Cd=="C",]$Dat_Flg1_Cd=1 #注意加','
trd[trd$Dat_Flg1_Cd!="C",]$Dat_Flg1_Cd=-1
trd$Dat_Flg1_Cd=as.numeric(trd$Dat_Flg1_Cd)
trd$cny_trx_amt_handled=trd$cny_trx_amt*trd$Dat_Flg1_Cd
trd.amount=tapply(trd$cny_trx_amt_handled,factor(trd$id),sum)
dfm=fuc.merge(dfm,trd.amount,'trd.amount')
dfm[is.na(dfm$trd.amount),]$trd.amount=0
ncol(dfm)==42+2
#交易分类取最高频Trx_Cod1_Cd,Trx_Cod2_Cd
Trx_Cod1_Cd.max=tapply(trd$Trx_Cod1_Cd,factor(trd$id),max)
Trx_Cod2_Cd.max=tapply(trd$Trx_Cod2_Cd,factor(trd$id),max)
dfm=fuc.merge(dfm,Trx_Cod1_Cd.max,'Trx_Cod1_Cd.max')
dfm=fuc.merge(dfm,Trx_Cod2_Cd.max,'Trx_Cod2_Cd.max')
#交易时间距end_time时长的均值和最小值:trd_time_delta_mea,trd_time_delta_min
trd$trx_tm=substring(trd$trx_tm,1,10)
trd$trx_tm=as.Date(trd$trx_tm)
endtime=as.Date("2019-06-30")
trd$trd_time_delta=endtime-trd$trx_tm #endtime可以广播
trd$trd_time_delta=as.integer(trd$trd_time_delta)
trd_time_delta.mean=tapply(trd$trd_time_delta,factor(trd$id),mean)
trd_time_delta.min=tapply(trd$trd_time_delta,factor(trd$id),min)
dfm=fuc.merge(dfm,trd_time_delta.mean,'trd_time_delta.mean')
dfm=fuc.merge(dfm,trd_time_delta.min,'trd_time_delta.min')
#支付方式Dat_Flg3_Cd
trd[trd$Dat_Flg3_Cd=="A",]$Dat_Flg3_Cd=1
trd[trd$Dat_Flg3_Cd=="B",]$Dat_Flg3_Cd=2
trd[trd$Dat_Flg3_Cd=="C",]$Dat_Flg3_Cd=3
trd$Dat_Flg3_Cd=as.numeric(trd$Dat_Flg3_Cd)
Dat_Flg3_Cd.mean=tapply(trd$Dat_Flg3_Cd,factor(trd$id),mean)
Dat_Flg3_Cd.mean=data.frame(Dat_Flg3_Cd.mean)
Dat_Flg3_Cd.mean=round(Dat_Flg3_Cd.mean)
Dat_Flg3_Cd.mean[Dat_Flg3_Cd.mean==1]="A"
Dat_Flg3_Cd.mean[Dat_Flg3_Cd.mean==2]="B"
Dat_Flg3_Cd.mean[Dat_Flg3_Cd.mean==3]="C"
dfm=fuc.merge(dfm,Dat_Flg3_Cd.mean,'Dat_Flg3_Cd.mean')

##2.2提取beh的特征

#使用app次数beh.count
beh$count=1
beh.count=tapply(beh$count, factor(beh$id), sum)
dfm=fuc.merge(dfm,beh.count,'beh.count')
dfm[is.na(dfm$beh.count),]$beh.count=0
#使用频率最高页面
tapply(beh$count, list(factor(beh$id),factor(beh$page_no)), max)
#可以看出界面的聚集程度不够高，因此放弃最高频页面的统计
#交易时间距end_time时长的均值和最小值:trd_time_delta_mea,trd_time_delta_min
beh$page_tm=substring(beh$page_tm,1,10)
beh$page_tm=as.Date(beh$page_tm)
endtime=as.Date("2019-06-30")
beh$beh_time_delta=endtime-beh$page_tm #endtime可以广播
beh$beh_time_delta=as.integer(beh$beh_time_delta)
beh_time_delta.mean=tapply(beh$beh_time_delta,factor(beh$id),mean)
beh_time_delta.min=tapply(beh$beh_time_delta,factor(beh$id),min)
dfm=fuc.merge(dfm,beh_time_delta.mean,'beh_time_delta.mean')
dfm=fuc.merge(dfm,beh_time_delta.min,'beh_time_delta.min')
#检验
ncol(dfm)==42+10
nrow(dfm)==43923
dfm1=dfm

###2.3 特征分类

#object类
one_hot_list=c('ic_ind','gdr_cd','mrg_situ_cd','atdd_type','l1y_crd_card_csm_amt_dlm_cd','crd_card_act_ind','hld_crd_card_grd_cd','edu_deg_cd','loan_act_ind','acdm_deg_cd','fr_or_sh_ind','dnl_mbl_bnk_ind','dnl_bind_cmb_lif_ind','hav_car_grp_ind','hav_hou_grp_ind','l6mon_agn_ind','fin_rsk_ases_grd_cd','confirm_rsk_ases_lvl_typ_cd','cust_inv_rsk_endu_lvl_cd','deg_cd','tot_ast_lvl_cd','pot_ast_lvl_cd','vld_rsk_ases_ind')
object_to_num=c('his_lng_ovd_day','ovd_30d_loan_tot_cnt','l12_mon_gld_buy_whl_tms','l12_mon_insu_buy_whl_tms','l12_mon_fnd_buy_whl_tms','l12mon_buy_fin_mng_whl_tms','job_year','frs_agn_dt_cnt','trd_time_delta.mean','trd_time_delta.min','beh_time_delta.mean','beh_time_delta.min')
#int类
normal_int_list=c('age','cur_credit_min_opn_dt_cnt','cur_debit_cnt','cur_debit_min_opn_dt_cnt','cur_credit_cnt')
one_hot_int_list=c('l6mon_daim_aum_cd','pl_crd_lmt_cd','bk1_cur_year_mon_avg_agn_amt_cd','perm_crd_lmt_cd','cur_debit_crd_lvl')
#附加类
one_hot_more=c('Trx_Cod1_Cd.max','Trx_Cod2_Cd.max','Dat_Flg3_Cd.mean')
# #int汇总
train_int_list=c(normal_int_list,one_hot_int_list)
#one_hot汇总
object_to_onehot=c(one_hot_list,one_hot_more)


######3 观察数据


#3.1 查看NULL在各变量中的个数

sapply(dfm1,function(x) sum(is.na(x)))

#3.2 查看int类型变量的分布

library(ggplot2)
# ggplot(dfm1, aes(x =dfm1[,c(normal_int_list[1])] ))+
#   # 密度曲线函数：alpha设置填充色透明度
#   geom_density(alpha = 0.3)

# for (each in normal_int_list){
#   ggplot(dfm1, aes(x =dfm1[,c(each)] ))+
#     # 密度曲线函数：alpha设置填充色透明度
#     geom_density(alpha = 0.3)
#   print(each)
# }

ggplot(dfm1, aes(x = age))+ geom_density(alpha = 0.3)
ggplot(dfm1, aes(x = cur_credit_min_opn_dt_cnt))+ geom_density(alpha = 0.3)
ggplot(dfm1, aes(x = cur_debit_cnt))+ geom_density(alpha = 0.3)
ggplot(dfm1, aes(x = cur_debit_min_opn_dt_cnt))+ geom_density(alpha = 0.3)
ggplot(dfm1, aes(x = cur_credit_cnt))+ geom_density(alpha = 0.3)
#可以看出cur_debit_cnt和cur_credit_cnt的偏度比较大，下一步对两者两次取对数

#3.3 其他观察数据：略


######4 处理数据


###4.1 处理偏度较大的变量

dfm.log=dfm1
dfm.log$cur_debit_cnt=log(log(1+dfm.log$cur_debit_cnt)+1)
ggplot(dfm.log, aes(x = cur_debit_cnt))+ geom_density(alpha = 0.3)
dfm.log$cur_credit_cnt=log(log(1+dfm.log$cur_credit_cnt)+1)
ggplot(dfm.log, aes(x = cur_credit_cnt))+ geom_density(alpha = 0.3)
#从分布可以看出偏度已经得到改善
dfm1$cur_debit_cnt=dfm.log$cur_debit_cnt
dfm1$cur_credit_cnt=dfm.log$cur_credit_cnt


###4.2 object_to_num中将object变成num，然后将其中的/N换成列均值


dfm2=dfm1
for(i in object_to_num){
  #观察object_to_num这些列的数据发现所有值除了内含为数字的字符串外
  #，其他均是‘\\N’，因此可以忽略强制转换导致的warning
  dfm2[,i]=as.numeric(dfm2[,i])
  dfm2[,i][is.na(dfm2[,i])]= mean(dfm2[,i],na.rm=T)
}

###4.3 处理int或float列中的na

# 处理类型为object的列中'\\N'，
for (i in c(train_int_list,object_to_num)){
  dfm2[,i][is.na(dfm2[,i])]=mean(dfm2[,i],na.rm = T)
}
dfm2[is.na(dfm2)]='na'

###4.4 one-hot

fuc.onehot=function(df=dfm2,one_hot_list=object_to_onehot){
  library(dplyr)
  dfm.cusum=select_if(df,is.numeric)
  for (j in one_hot_list){
    df.onehot=as.data.frame(model.matrix(~get(j)-1,df))
    tail=substring(colnames(df.onehot),7,50)
    colnames(df.onehot)=paste(j,tail)
    dfm.cusum=cbind(dfm.cusum,df.onehot)
  }
  
  return(dfm.cusum)
}
dfm3=fuc.onehot()

###4.5 训练集train 评分集pred

nrow(dfm3)==43923
length(colnames(select_if(dfm2,is.numeric)))+length(object_to_onehot)==ncol(dfm2)-1
dfm3=cbind(dfm2$id,dfm3)
colnames(dfm3)[1]='id'
train.tag1=read.csv('C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\训练数据集\\训练数据集\\训练数据集_tag.csv',header=TRUE,stringsAsFactors=F)
train.raw=as.data.frame(train.tag1[,c('id','flag')])
colnames(train.raw)=c('id','flag')
train.final=merge(train.raw,dfm3,by='id',all.x=TRUE)
train.final=train.final[ ,!names(train.final) %in% c('id')]
nrow(train.final)==nrow(train.tag1)
ncol(train.final)

pred.raw=as.data.frame(pred.tag$id)
colnames(pred.raw)='id'
pred=merge(pred.raw,dfm3,by='id',all.x=TRUE)
pred=pred[ ,!names(pred) %in% c('id')]
nrow(pred)==nrow(pred.tag)
ncol(pred)+1==ncol(train.final)

#保存
write.csv(train.final,"C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\train_final.csv")
write.csv(pred,"C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\pred.csv")


###### 5 构建逻辑回归模型


n=nrow(train.final)
set.seed(996) 
rnd<-sample(n,n*.70)

train<-train.final[rnd,]

test<-train.final[-rnd,]

#5.1使用向前逐步法进行逻辑回归建模

model<-glm(flag~.,data=train,family = binomial(link=logit),control=list(maxit=25))

# Warning message:
#   glm.fit:拟合機率算出来是数值零或一
# 拟合概率算出来的概率为0或1，可能是由于样本数据是线性可分的，
# 这时logistic回归往往会导致过拟合的问题，因此采用逻辑回归来预测就不太适用
# ，而直接使用规则判断的方法会更简单且适用。

#5.2 绘制拟合概率图

p<-predict(model,type='response')
pp=as.data.frame(p)
p0=pp[pp$p<=0.5,]
p1=pp[pp$p>0.5,]
library(ggplot2)
qplot(seq(-100,100,length=length(p)),sort(p),ylab='predict0-1',main = '拟合概率图0-1')
qplot(seq(-100,100,length=length(p0)),sort(p0),ylab='predict0-0.5',main = '拟合概率图0-0.5')
qplot(seq(-100,100,length=length(p1)),sort(p1),ylab='predict0.5-1',main = '拟合概率图0.5-1')

#5.3 使用向前逐步法进行逻辑回归建模

forward_model<-step(model,direction="forward")
summary(forward_model)


###### 6 模型评估


#用测试集做模型评估

pre<-predict(forward_model,test,type="response")

#在预测数据集中，概率大于0.5,违约，概率小于0.5，不违约

test$pre_flag<-ifelse(predict(forward_model,test,type="response")>0.5,1,0)

table(test$flag,test$pre_flag)

#6.1 测试集准确率计算

sum_diag<-sum(diag(table(test$flag,test$pre_flag)))

sum<-sum(table(test$flag,test$pre_flag))

accuracy<-sum_diag/sum
cat('-------------------')
cat('测试集精确度accuracy：',accuracy)

#用测试集做模型评估

pre.train<-predict(forward_model,train,type="response")

#在预测数据集中，概率大于0.5,违约，概率小于0.5，不违约

train.pre_flag<-ifelse(predict(forward_model,train,type="response")>0.5,1,0)

table(train$flag,train.pre_flag)

#6.2 训练集准确率计算

sum_diag<-sum(diag(table(train$flag,train.pre_flag)))

sum<-sum(table(train$flag,train.pre_flag))

accuracy<-sum_diag/sum
cat('-------------------')
cat('训练集精确度accuracy：',accuracy)

#6.3 ROC曲线评估

# install.packages("ROCR") 
library(ROCR)

pred_forauc=prediction(pre,test$flag)
pred_forauc <- prediction(pre,test$flag)   #预测值(0.5二分类之前的预测值)和真实值    
performance(pred_forauc,'auc')@y.values        #AUC值 
perf <- performance(pred_forauc,'tpr','fpr')  #y轴为tpr(true positive rate),x轴为fpr(false positive rate)
plot(perf,main='ROC curve') 


######7 模型预测及应用


#预测
pred$predict<-predict(forward_model,pred,type="response")
pred$pre_flag<-ifelse(pred$predict>0.5,1,0)
result=cbind(pred.tag$id,pred[,c('predict','pre_flag')])
write.csv(result,"C:\\Users\\Huiqin Xie\\Desktop\\暑期实习申请\\面试资料\\蓝色光标数据挖掘\\result.csv")
