#include "kline.h"
#include "listFiles.h"
using namespace std;
#include <fstream>
#include<algorithm>
#include <cstdlib>
#include <filesystem>
namespace fs = std::filesystem;


//自定义排序函数  
bool sortFun(const tick &p1, const tick &p2)
{
	return p1.DoubleTime < p2.DoubleTime;//升序排列  
}


void mainKL(int minN,string cinDate,bool willZip ,bool willRemove)
{
string tempPath = "/home/xiehq/dmgrl2/temp/tick/";
string tickPath = "/var/L2/"+cinDate+"/SSEL2/STOCK/TAQ/"; 
string SavePath =  makeDir("/home/xiehq/klineDB/" +cinDate+"/"); //makeDir(tempPath +cinDate+"/");
string csvPath = makeDir(tempPath + "csv"+cinDate+"/");
cout<<"******************"<<intToString(minN)<<"minKline begin"<<"******************"<<endl;
if(willZip)
{
	//unzip 解压普通压缩包
	vector<string> zipFiles;
	getFiles(tickPath , zipFiles ,false);
	for(auto zipIt = zipFiles.begin();zipIt != zipFiles.end();zipIt++)
	{
		if(zipIt->find(".zip") == (int)string::npos) continue;
		string unzipStr = "unzip -od "+csvPath+" "+(*zipIt); //+" > /dev/null";
		system(unzipStr.c_str());
	}
	cout<<"#################"<<"unzip done"<<"#################"<<endl;
}

//获取目标时间戳
vector<std::string> timeStrVec;
getKlineTimeStr(minN,cinDate ,timeStrVec);
//读取原数数据
vector<string> files;
getFiles(csvPath , files ,false);
string outCsvPath = SavePath+"kline_"+intToString(minN)+"min_"+cinDate+".csv";
ofstream p;
p.open(outCsvPath.c_str(),ios::out); 
p<<"StockID"<<","<<"StockName"<<","<<"sepDateTime"<<","<<"Expr1"<<","<<"price"<<","<<"open"<<","<<"high"<<","<<"low"<<\
		","<<"vol"<<","<<"amount"<<","<<"cjbs"<<","<<"yclose"<<","<<"Time"<<endl;   
// cout<<"NO."<<"StockID"<<","<<"StockName"<<","<<"sepDateTime"<<","<<"Expr1"<<","<<"price"<<","<<"open"<<","<<"high"<<","<<"low"<<\
// 		","<<"vol"<<","<<"amount"<<","<<"cjbs"<<","<<"yclose"<<","<<"Time"<<endl;   
p.close();  
//测试只读前5个文件 testN
// int testN = 0;
for(auto vit = files.begin();vit != files.end() ;vit++)
{
	// if(testN >5) break;
	// testN++;
    if(vit->find(".csv") == (int)string::npos) continue;
	// cout << *vit <<"-----"<<intToString(minN)<<"min"<<endl;
	vector<tick> v;

    ifstream ifs;
	ifs.open(vit->c_str());
	if (!ifs.is_open())	
    {
		cout<<"Open Error:"<<vit->c_str()<<" open failed"<<endl;
		continue;
    }
	string  line;
	int rowN = 0;
	while(getline(ifs,line))
    {
		tick tk;
		if (rowN >0 && line.size() > 0 )
		{
			if(readTickCsv(line,tk)) v.push_back(tk);
		}
		rowN++;
	}
	ifs.close();
	sort(v.begin(), v.end(), sortFun);

    p.open(outCsvPath.c_str(),ios::out|ios::app);     //打开文件路径 
	p.setf(ios::fixed, ios::floatfield);  // 设定为 fixed 模式，以小数点表示浮点数
	p.precision(2);  // 设置小数位数2

    
	int cN = 0;
	double yclose = 0;
	for(auto it = v.begin();it!=v.end();it++)
	{
		if(it->PreClosePrice >0) { yclose= it->PreClosePrice;break;}
	}
	
	auto newBegin = v.begin();
	for(auto tt = timeStrVec.begin();tt < timeStrVec.end();tt++) 
	{
		double dtt = atof(tt->c_str());
		if(tt->substr(8,6) == "113000" || tt->substr(8,6) == "150000" ) //11:00:00 + 30min,15:00:00 + 30min
		{
			dtt += 3000;
		}
		kline kl;
		vector<double> highVec;
		vector<double> lowVec;
		if(newBegin->Symbol.substr(0,1) == "6") kl.StockID = "SH" + newBegin->Symbol;
		else kl.StockID = "SZ" + newBegin->Symbol;
		kl.StockName = "name";
		kl.sepDateTime = qts::utils::systp2rep(qts::utils::to_time_point(*tt));
		kl.Expr1 = tt->substr(0,4) + "-" +tt->substr(4,2)+"-"+tt->substr(6,2)+" "+\
					tt->substr(8,2)+":"+tt->substr(10,2)+":"+tt->substr(12,2);
		kl.yclose = yclose;
		kl.Time = (tt->substr(tt->find(".") -6,6)).insert(2,":").insert(5,":");
		bool openInput = false;
		bool noData = true;
		for(auto vt = newBegin;vt != v.end();vt++)
		{
			if(vt->DoubleTime < dtt)
			{
				noData = false;
				if(openInput == false && vt->TotalVolume >0 && vt->OpenPrice > 0) 
				{kl.open = vt->OpenPrice;openInput = true;}
				highVec.push_back(vt->HighPrice);
				if(vt->TotalVolume >0) lowVec.push_back(vt->LowPrice);	
				if(vt != v.begin())
				{
					kl.vol += (vt->TotalVolume) - ((vt-1)->TotalVolume);
					kl.amount += (vt->TotalAmount) - ((vt-1)->TotalAmount);
					kl.cjbs += (vt->TotalNo) - ((vt-1)->TotalNo);
				}
				else
				{
					kl.vol += (vt->TotalVolume);
					kl.amount += (vt->TotalAmount);
					kl.cjbs += (vt->TotalNo);
				}	
				newBegin++;	
			}
			else 
			{
				if(noData) cout<<"Data Error:"<<kl.StockID<<"_"<<kl.Expr1<<" have no data"<<endl;
				break;
			}
		}
		if(highVec.size() > 0)	kl.high = *max_element(highVec.begin(), highVec.end()); 
		if(lowVec.size() > 0)	kl.low = *min_element(lowVec.begin(), lowVec.end());
		yclose = kl.price = (newBegin-1)->LastPrice;
		//输出每行
		p<<kl.StockID<<","<<kl.StockName<<","<<kl.sepDateTime<<","<<kl.Expr1<<","<<kl.price<<","<<kl.open<<","<<kl.high<<","<<kl.low<<\
			","<<kl.vol<<","<<kl.amount<<","<<kl.cjbs<<","<<kl.yclose<<","<<kl.Time<<endl;   
		// cout.setf(ios::fixed);
		// cout.precision(2); // 精度为输出小数点后2位
		// cout<<cN<<","<<kl.StockID<<","<<kl.StockName<<","<<kl.sepDateTime<<","<<kl.Expr1<<","<<kl.price<<","<<kl.open<<","<<kl.high<<","<<kl.low<<\
		// 	","<<kl.vol<<","<<kl.amount<<","<<kl.cjbs<<","<<kl.yclose<<","<<kl.Time<<endl;   
		// cN ++;

	}
	p.close();

}
if(willRemove) fs::remove_all(csvPath.c_str());
cout<<"#################"<<intToString(minN)<<"minKline succeed"<<"#################"<<endl;
}




/*

int main()
{
string cinDate = "20201113";
mainKL(1,cinDate,true,false);
mainKL(5,cinDate,false,false);
mainKL(15,cinDate,false,false);
mainKL(30,cinDate,false,true);
return 0;
}

*/