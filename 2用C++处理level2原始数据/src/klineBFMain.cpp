#include "kline.h"
#include "listFiles.h"
using namespace std;
#include <fstream>
#include<algorithm>
#include <cstdlib>
#include <filesystem>
#include <unordered_map>
namespace fs = std::filesystem;
#include<ctime>
#include <iostream>
extern ofstream klineBFErr;

//自定义排序函数  
bool sortFun(const tick &p1, const tick &p2)
{
	return p1.DoubleTime < p2.DoubleTime;//升序排列  
}


void mainKL(int minN,string cinDate,bool willZip ,bool willRemove)
{
string tempPath = "/home/xiehq/dmgrl2/temp/tick/";
string tickPath = "/var/L2/"+cinDate+"/SSEL2/STOCK/TAQ/"; 
string SavePath =  makeDir("/var/L2/klineBF/"); //makeDir(tempPath +cinDate+"/");
string csvPath = makeDir(tempPath + "csv"+cinDate+"/");
cout<<"******************"<<intToString(minN)<<"minKline begin--"<<cinDate<<"******************"<<endl;
clock_t startTime;
startTime = clock();//计时开始	
bool zipExist = false;
vector<string> zipFiles;
if(willZip)
{
	//unzip 解压普通压缩包
	getFiles(tickPath , zipFiles ,false);
	for(auto zipIt = zipFiles.begin();zipIt != zipFiles.end();zipIt++)
	{
		if(zipIt->find(".zip") == (int)string::npos) continue;
		zipExist = true;
		string unzipStr = "unzip -od "+csvPath+" "+(*zipIt); //+" > /dev/null";
		if(system(unzipStr.c_str()) == -1)
        {
            klineBFErr<<"Unzip Error--"<<unzipStr<<endl;
	        cout<<"////////////////// "<<"unzip failed"<<" ////////////////"<<endl;
        }
        else cout<<"#################"<<"unzip done"<<"#################"<<endl;
	}
	
}
else zipExist = true;

//获取9:15- 9:25目标时间戳
vector<std::string> timeStrVec;
getKlineBFTimeStr(minN,cinDate ,timeStrVec);
//读取原数数据
vector<string> files;
if(zipExist) getFiles(csvPath , files ,false);
else getFiles(tickPath , files ,false);
string outCsvPath = SavePath+"klineBF_"+intToString(minN)+"min_"+cinDate+".csv";
ofstream p;
p.open(outCsvPath.c_str(),ios::out); 
p<<"StockID"<<","<<"StockName"<<","<<"sepDateTime"<<","<<"Expr1"<<","<<"price"<<","<<"open"<<","<<"high"<<","<<"low"<<\
		","<<"askVol"<<","<<"bidVol"<<","<<"yclose"<<","<<"Time"<<endl;   
p.close();  
double skipDoubleTime = atof(timeStrVec.begin()->c_str());
double DoubleCinDate = atof(cinDate.c_str());
double doubleLastTick = DoubleCinDate*1000000.0+92500.0;
for(auto vit = files.begin();vit != files.end() ;vit++)
{
	cout<<*vit<<endl;


    if(vit->find(".csv") == (int)string::npos) continue;
	// cout << *vit <<"-----"<<intToString(minN)<<"min"<<endl;
	vector<tick> v;

    ifstream ifs;
	ifs.open(vit->c_str());
	if (!ifs.is_open())	
    {
		klineBFErr<<"Open Error:"<<vit->c_str()<<" open failed"<<endl;
		continue;
    }
	string  line;
	int rowN = 0;
	while(getline(ifs,line))
    {
		tick tk;
		if (rowN >0 && line.size() > 0 && rowN < 200 )
		{
			if(readTickCsvBF(line,tk)) v.push_back(tk);
		}
		rowN++;
	}
	ifs.close();

	if(v.size() < 1){klineBFErr<<*vit<<"--have no data"<<endl;continue;}
	sort(v.begin(), v.end(), sortFun);
    p.open(outCsvPath.c_str(),ios::out|ios::app);     //打开文件路径 
	p.setf(ios::fixed, ios::floatfield);  // 设定为 fixed 模式，以小数点表示浮点数
	p.precision(2);  // 设置小数位数2

	string symbol = "NULL";
	if(vit->length() <10)	
	{
		symbol = vit->substr(vit->length()-10,6);
		for(int si =0;si<6;si++) 
		{
			if(isdigit(symbol[si]) == 0) 
			{
				for(auto it =v.begin();it != v.end();it++)
				{
					if(it->Symbol.length() == 6) 
					{
						symbol = it->Symbol;
						break;
					
					}
				}
				break;
			}
		}	
	}
	else
	{
		for(auto it =v.begin();it != v.end();it++)
		{
			if(it->Symbol.length() == 6) 
			{
				symbol = it->Symbol;
				break;
			
			}
		}
	}

	if(symbol =="NULL") 
	{
		klineBFErr<<"Symbol Error--NULL"<<*vit<<endl;	
	}

	
	double yclose = 0;
	for(auto it = v.begin();it!=v.end();it++)
	{
		if(it->PreClosePrice >0) { yclose= it->PreClosePrice;break;}
	}
	

	auto newBegin = v.begin();
	
	kline lastKL;
	for(auto tt = timeStrVec.begin();tt != timeStrVec.end();tt++) 
	{
		
		double dtt = atof(tt->c_str());
		kline kl;
		vector<double> highVec;
		vector<double> lowVec;
		string frt = symbol.substr(0,1);
		if(frt == "6") kl.StockID = "SH" + symbol;
		else if(frt == "0" || frt == "3") kl.StockID = "SZ" + symbol;
		else kl.StockID = symbol;
		kl.StockName = "name";
		kl.sepDateTime = qts::utils::systp2rep(qts::utils::to_time_point(*tt));
		if(tt->length() <14)
		{
			klineBFErr<<"timeStrVec Length Error--tt->length() <14"<<symbol<<"--"<<*tt<<endl;
			continue;
		}
		kl.Expr1 = tt->substr(0,4) + "-" +tt->substr(4,2)+"-"+tt->substr(6,2)+" "+\
					tt->substr(8,2)+":"+tt->substr(10,2)+":"+tt->substr(12,2);
		kl.yclose = yclose;
		kl.Time = (tt->substr(tt->find(".") -6,6)).insert(2,":").insert(5,":");
		// bool openInput = false;
		bool noData = true;
		int count  = 0;
		kl.open = newBegin->OpenPrice;
		bool isLastTick = false;
		for(auto vt = newBegin;vt != v.end();vt++)
		{
			if(vt->DoubleTime <= dtt)
			{
				if(vt->DoubleTime - doubleLastTick <=0.0001 ) 
				{
					kl.price = newBegin->DoubleTemp;
					isLastTick = true;
					break;
				}
				noData = false;
				// if(openInput == false ) 
				// {kl.open = vt->OpenPrice;openInput = true;}
				highVec.push_back(vt->HighPrice);
				lowVec.push_back(vt->LowPrice);	
				kl.bidVol += vt->BuyVolumeSum;
				kl.askVol += vt->SellVolumeSum;
				newBegin++;	
				count++;
			}
			else 
			{
				// if(noData) klineBFErr<<"Data Error:"<<kl.StockID<<"_"<<kl.Expr1<<" have no data"<<endl;
				kl.price = (newBegin-1)->LastPrice;
				break;
			}
		}
		kl.askVol /= count;
		kl.bidVol /= count;
		if(highVec.size() > 0)	kl.high = *max_element(highVec.begin(), highVec.end()); 
		if(lowVec.size() > 0)	kl.low = *min_element(lowVec.begin(), lowVec.end());
		
		//输出每行
		if(dtt != skipDoubleTime && (!noData))
		{
			
			if(kl.askVol+kl.bidVol == 0 && kl.high == 0 && tt!= timeStrVec.begin() +1) 
			{
				p<<kl.StockID<<","<<kl.StockName<<","<<kl.sepDateTime<<","<<kl.Expr1<<","<<lastKL.price<<","<<lastKL.open<<","<<lastKL.high<<","<<lastKL.low<<\
					","<<lastKL.askVol<<","<<lastKL.bidVol<<","<<yclose<<","<<kl.Time<<endl;  
				yclose = lastKL.price;
			}
			else
			{
				p<<kl.StockID<<","<<kl.StockName<<","<<kl.sepDateTime<<","<<kl.Expr1<<","<<kl.price<<","<<kl.open<<","<<kl.high<<","<<kl.low<<\
					","<<kl.askVol<<","<<kl.bidVol<<","<<yclose<<","<<kl.Time<<endl;   
				yclose = kl.price;
				lastKL = kl; //重载kline operator= ;深拷贝;
			}

			if(!isLastTick)
			{
				if(kl.price > kl.high) klineBFErr<<"Logical Error1--kl.price > kl.high"<<*vit<<"--"<<*tt<<endl;
				if((kl.askVol+kl.bidVol == 0 && kl.high != 0)|| (kl.askVol+kl.bidVol != 0 && kl.high == 0)) klineBFErr\
							<<"Logical Error2--(kl.askVol+kl.bidVol == 0 && kl.high != 0)||(kl.askVol+kl.bidVol != 0 && kl.high == 0) "\
							<<*vit<<"--"<<*tt<<endl;
			}
			
		}
	}
	p.close();

}
if(willRemove) fs::remove_all(csvPath.c_str());
cout << "The run time is: " <<(double)(clock() - startTime) / CLOCKS_PER_SEC << "s" << endl;
cout<<"#################"<<intToString(minN)<<"minKline succeed"<<"#################"<<endl;
}





int main()
{
///var/L2$ 
string sysT = getSysTime(false);
string tpPath = makeDir("/var/L2/klineBF/");
string errPath = tpPath + "Error.txt";
klineBFErr.open(errPath);
klineBFErr<<sysT<<endl;
vector<string> dateFiles;
getFiles1Step("/var/L2/",dateFiles,false);
for(auto vt = dateFiles.begin();vt != dateFiles.end();vt++)
{
if(vt->length() != 8) continue;
mainKL(1,*vt,true,true);
}
// mainKL(1,"20201124",false,false);
return 0;
}

// if(system("head -n 100 /home/xiehq/klineDB/BF/20201113/klineBF_1min_20201113.csv > /home/xiehq/dmgrl2/temp/testRes.csv") == -1)
// cout<<"system failed"<<endl;