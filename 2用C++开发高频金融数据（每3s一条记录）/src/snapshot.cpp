
#include "snapshot.h"
#include "compress.h"
using namespace qts;
using namespace qts::utils;
using namespace std;
#include <filesystem>
#include <fstream>
#include <exception>
namespace fs = std::filesystem;
//ofstream err("/home/xiehq/dmgrl2/temp/error.txt");
ofstream ofsErr;
unordered_map<int,int> tkMap;
#include "kline.h"

bool readSnapshot(string &line , snapshot &ss)
{
	vector<char *> vec;
	lineToCharStarVec(line,vec);
	//跳过非本交易所A股的数据
	if(string(vec[0]).length() <1) return false;
	int intID = atoi(vec[0]);
	if((int)(intID/100000) != 6) return false;
	if(tkMap.count(intID) == 0)  return false;
	//检查列数
	bool XTP;
	if(vec.size() == 194)  XTP= false;
	else if(vec.size() == 174) XTP = true;
	else
	{
		if(vec.size() >= 2)	
		{
			cerr<< "Columns Error:readSnapshot__"<<vec[0]<<"_"<<vec[1]<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSnapshot__"<<vec[0]<<"_"<<vec[1]<<"_"<<vec.size()<<endl;
		}
		else
		{
			cerr<< "Columns Error:readSnapshot"<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSnapshot"<<"_"<<vec.size()<<endl;
		}
		return false;
	}

	
	int n = 0;
	ss.intID = intID;
	//ss.SecurityID = vec[n];
	n++;
	string dateTimeStr = string(vec[n]) + ".000";
	stringToRep(dateTimeStr,ss.DateTime);n++;
	ss.PreClosePx = atof(vec[n]);n++;
	ss.OpenPx = atof(vec[n]);n++;
	ss.HighPx = atof(vec[n]);n++;
	ss.LowPx = atof(vec[n]);n++;
	ss.LastPx = atof(vec[n]);n++;
	ss.TotalVolumeTrade = atof(vec[n]);n++;
	ss.TotalValueTrade = atof(vec[n]);n++;
	strcpy(ss.InstrumentStatus ,vec[n]);n++;
	for (int j = 0;j <10;j++)
	{
		ss.BidPrice[j] = atof(vec[n]);
		n++;
	}
	for (int j = 0;j<10;j++)
	{	
		ss.BidOrderQty[j] = atof(vec[n]);
		n++;
	}
	
	
	if(!XTP)
	{
		for (int j = 0;j<10;j++)
		{	
			ss.BidNumOrders[j] = atof(vec[n]);
			n++;
		}
	}
	for (int j = 0;j<50;j++)
	{
		ss.BidOrders[j] = atof(vec[n]);
		n++;
	}
	for (int j = 0;j<10;j++)
	{	
		ss.OfferPrice[j] = atof(vec[n]);
		n++;
	}
	for (int j = 0;j<10;j++)
	{
		ss.OfferOrderQty[j] = atof(vec[n]);
		n++;
	}
	
	if(!XTP)
	{
		for (int j = 0;j<10;j++)
		{
			ss.OfferNumOrders[j] = atof(vec[n]);
			n++;
		}
	}

	for (int j = 0;j<50;j++)
	{
		ss.OfferOrders[j] = atof(vec[n]);
		n++;
	}
	ss.NumTrades = atof(vec[n]);n++;
	//IOPV
	n++;
	ss.TotalBidQty = atof(vec[n]);n++;
	ss.TotalOfferQty = atof(vec[n]);n++;
	ss.WeightedAvgBidPx = atof(vec[n]);n++;
	ss.WeightedAvgOfferPx = atof(vec[n]);n++;
	ss.TotalBidNumber = atof(vec[n]);n++;
	ss.TotalOfferNumber = atof(vec[n]);n++;
	ss.BidTradeMaxDuration = atof(vec[n]);n++;
	ss.OfferTradeMaxDuration = atof(vec[n]);n++;
	ss.NumBidOrders = atof(vec[n]);n++;
	ss.NumOfferOrders = atof(vec[n]);n++;
	ss.WithdrawBuyNumber = atof(vec[n]);n++;
	ss.WithdrawBuyAmount = atof(vec[n]);n++;
	ss.WithdrawBuyMoney = atof(vec[n]);n++;
	ss.WithdrawSellNumber = atof(vec[n]);n++;
	ss.WithdrawSellAmount = atof(vec[n]);n++;
	ss.WithdrawSellMoney = atof(vec[n]);n++;
	if(n != 188 &&n!=168) 
	{
		cerr << "Read SH Error：188(168) != "<<n<<endl;
		cout << "Read SH Error：188(168) != "<<n<<endl;
	}
	if(!XTP) return n==188;
	else return n == 168;
	
	
}

void stringToRep(const string &word ,systp::rep &l)
{

	l = qts::utils::systp2rep(qts::utils::to_time_point(word));
}

void stringToDouble(string &word , double &f)
{
	f = atof(word.c_str());
}

void writeSnapshot(const string &date, const unordered_map<int , vector<snapshot>> &m,const string &savePath)
{
	for(auto mit = m.begin();mit!=m.end();mit++)
	{
		const char* str = (const char*)(&mit->second[0]);		
    	size_t N = (size_t)(sizeof(snapshot) * mit->second.size());
		//mkdir,pay attention to dir exist
		string strTp = to_string(mit->first);	
		string strID = changeStrLen(6,strTp);
		string mkdir =  savePath + strID.substr(0,3)+"/"+strID.substr(3);
		// cout << mkdir <<endl;
		if(!fs::exists(mkdir))
		{
			fs::create_directories(mkdir);
		}
		const std::string filename = mkdir+"/"+ strID+ "_"+ date +".snap";	
		if(!compresswrite(filename,str,N))
			{
				cerr<<"compress failed"<<endl;
				cout<<"compress failed"<<endl;	
			}
		// cout<<"write--"<<mit->first<<endl;
			
	}
	
}
string changeStrLen(int tarTen ,const string &initString){
	int len  = initString.length();
	if(len < tarTen ){
		string zeros;
		for(int times  = 0;times < (tarTen - len) ;times ++)
		{
			zeros += "0";
		}
		return zeros + initString;
	}
	else if(len == tarTen )
	{
		return initString;
	}
	else if(len > tarTen)
	{
		return initString.substr(0,tarTen);
	}
	cerr<<"ChangeStrLen error"<<endl;
	cout<<"ChangeStrLen error"<<endl;
	return initString;

}

bool readSZBFTable3(string &line , snapshot &ss)
{
	vector<char *> vec;
	lineToCharStarVec(line,vec,'\t');
	if(vec.size() != 20) 
	{
		if(vec.size() >=3)	
		{
			cerr<< "Columns Error:readSZBFTable3__"<<string(vec[2])<<"_"<<string(vec[0])+string(vec[1])<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZBFTable3__"<<string(vec[2])<<"_"<<string(vec[0])+string(vec[1])<<"_"<<vec.size()<<endl;		
		}
		else
		{
			cerr<< "Columns Error:readSZBFTable3"<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZBFTable3"<<"_"<<vec.size()<<endl;
		}
		return false;
	}
	if(string(vec[2]).length() <1) return false;
	int intID = atoi(vec[2]);
	int frt = (int)(intID/100000);
	if( frt != 3 && frt != 0) return false;
	if(tkMap.count(intID) == 0) return false;
	ss.intID = intID;
	string SENDTIME = changeStrLen(6,vec[1]);
	string tempDT = string(vec[0]) + SENDTIME + ".000";
	stringToRep( tempDT,ss.DateTime);
	ss.PreClosePx = atof(vec[4]);
	ss.OpenPx = atof(vec[5]);
	ss.HighPx = atof(vec[6]);
	ss.LowPx = atof(vec[7]);
	ss.LastPx = atof(vec[8]);
	ss.TotalVolumeTrade = atof(vec[10]);
	ss.TotalValueTrade = atof(vec[11]);
	ss.NumTrades = atof(vec[9]);
	ss.TotalBidQty = atof(vec[18]);
	ss.TotalOfferQty = atof(vec[16]);
	ss.WeightedAvgBidPx = atof(vec[19]);
	ss.WeightedAvgOfferPx = atof(vec[17]);
	return true;
}

bool readSZBFTable4(string &line , snapshot &ss)
{
	vector<char *> vec;
	lineToCharStarVec(line,vec,'\t');
	if(vec.size() != 50) 
	{
		if(vec.size() >=3)	
		{
			cerr<< "Columns Error:readSZBFTable4"<<"_"<<string(vec[0])+string(vec[1])<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZBFTable4"<<"_"<<string(vec[0])+string(vec[1])<<"_"<<vec.size()<<endl;
		}
		else
		{
			cerr<< "Columns Error:readSZBFTable4"<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZBFTable4"<<"_"<<vec.size()<<endl;
		}
		return false;
	}
	if(string(vec[2]).length() <1) return false;
	int intID = atoi(vec[2]);
	int frt = (int)(intID/100000);
	if( frt != 3 && frt != 0) return false;
	if(tkMap.count(intID) == 0) return false;

	for (int j = 0;j <10;j++)
	{
		ss.BidPrice[j] = atof(vec[14+j]);
	}
	for (int j = 0;j <10;j++)
	{
		ss.BidOrderQty[j] = atof(vec[34+j]);
	}
	ss.BidNumOrders[0] = atof(vec[44]);
	slashString(vec[46],ss.BidOrders);

	for (int j = 0;j <10;j++)
	{
		ss.OfferPrice[j] = atof(vec[13-j]);
	}
	for (int j = 0;j <10;j++)
	{
		ss.OfferOrderQty[j] = atof(vec[24+j]);
	}
	ss.OfferNumOrders[0] = atof(vec[47]);
	slashString(vec[49],ss.OfferOrders);
	return true;

}


void slashString(const string &str,double arr[],string sep,unsigned int slashIndex0,int i)
{
	if(str == sep || str == "" || slashIndex0 >= str.length()) return ;
	unsigned int slashIndex1 = str.find(sep,slashIndex0);
	if(slashIndex1 != (int)string::npos) //4294967295
	{	
		string str0 = str.substr(slashIndex0,slashIndex1 - slashIndex0 );
		arr[i] = atof(str0.c_str()) ;
	}
	else
	{
		string str0 = str.substr(slashIndex0);
		arr[i] = atof(str0.c_str());
		// cout<<slashIndex0<<"--"<<slashIndex1<<"--"<<arr[i]<<"--"<<i<<endl;	
		return ;
	}
	
	// cout<<slashIndex0<<"--"<<slashIndex1<<"--"<<arr[i]<<"--"<<i<<endl;
	
	slashIndex0= slashIndex1 +1;
	i++;
	slashString(str,arr,sep,slashIndex0,i);

}


vector<string> lineToVec(string &line,const char &sep)
{
	char buff[1000];
	int p =0;
	vector<string> vec;
	vec.reserve(200);
	for (int i =0;i <line.size();i++)
	{
		if (line[i] != sep)
		{
			buff[p++] = line[i];
		}
		else{
			//buff[p]='\0';
			vec.emplace_back(buff,buff+p);
			p = 0;
		}
	}
	vec.emplace_back(buff,buff+p);
	// cout<<"本行vec("<<vec[0]<<"_"<<vec[1]<<")："<<vec.size()<<endl;
	return vec;
}


void lineToCharStarVec(std::string &line,std::vector<char *> &vec ,const char &sep)
{
	vec.reserve(200);
	bool isSep = true;
	int contN = 0;
	int i;
	for(i = 0;i<line.size();i++)
	{
		if(isSep)
		{
			vec.push_back(&line[i]);
		}
		if(line[i] == sep)
		{

			isSep = true;
			line[i] = '\0';
			contN++;
		}
		else isSep = false;

	}
	if(isSep) vec.push_back(&line[i]);
}


bool readSZAFTableHq(string &line , snapshot &ss)
{
	vector<char *> vec;
	lineToCharStarVec(line,vec,'\t');
	if(vec.size() < 32)
	{
		if(vec.size() >=7)	
		{
			cerr<< "Columns Error:readSZAFTableHq__"<<vec[6]<<"_"<<vec[1]<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZAFTableHq__"<<vec[6]<<"_"<<vec[1]<<"_"<<vec.size()<<endl;
		}
		else
		{
			cerr<< "Columns Error:readSZAFTableHq"<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZAFTableHq"<<"_"<<vec.size()<<endl;
		}
		return false;
	}
	int intID = atoi(vec[6]);
	if(string(vec[6]).length() <1) return false;
	int frt = (int)(intID/100000);
	if( frt != 3 && frt != 0) return false;
	if(tkMap.count(intID) == 0) return false;
	//ss.SecurityID  = changeStrLen(6,vec[6]);
	ss.intID = intID;
	string tempDT = changeStrLen(14,vec[1]) + ".000";
	stringToRep( tempDT,ss.DateTime);
	ss.PreClosePx = atof(vec[9]);
	ss.OpenPx = atof(vec[12]);
	ss.HighPx = atof(vec[13]);
	ss.LowPx = atof(vec[14]);
	ss.LastPx = atof(vec[15]);
	ss.TotalVolumeTrade = atof(vec[17]);
	ss.TotalValueTrade = atof(vec[18]);
	ss.NumTrades = atof(vec[16]);
	ss.TotalBidQty = atof(vec[24]);
	ss.TotalOfferQty = atof(vec[22]);
	ss.WeightedAvgBidPx = atof(vec[25]);
	ss.WeightedAvgOfferPx = atof(vec[23]);
	return true;

}

bool readSZAFTableLevel(string &line , snapshot &ss)
{
	vector<char *> vec;
	lineToCharStarVec(line,vec,'\t');
	if(vec.size() != 55) 
	{
		if(vec.size() >=7)	
		{
			cerr<< "Columns Error:readSZAFTableLevel__"<<vec[6]<<"_"<<vec[1]<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZAFTableLevel__"<<vec[6]<<"_"<<vec[1]<<"_"<<vec.size()<<endl;
		}
		else
		{
			cerr<< "Columns Error:readSZAFTableLevel"<<"_"<<vec.size()<<endl;
			cout<< "Columns Error:readSZAFTableLevel"<<"_"<<vec.size()<<endl;
		}
		return false;
	}
	if(string(vec[6]).length() <1) return false;
	int intID = atoi(vec[6]);
	int frt = (int)(intID/100000);
	if( frt != 3 && frt != 0) return false;
	if(tkMap.count(intID) == 0) return false;

	for (int j = 0;j <10;j++)
	{
		ss.BidPrice[j] = atof(vec[10+j*4]);
	}
	for (int j = 0;j <10;j++)
	{
		ss.BidOrderQty[j] = atof(vec[12+j*4]);
	}
	ss.BidNumOrders[0] = atof(vec[49]);
	slashString(vec[51],ss.BidOrders);

	for (int j = 0;j <10;j++)
	{
		ss.OfferPrice[j] = atof(vec[9+j*4]);
	}
	for (int j = 0;j <10;j++)
	{
		ss.OfferOrderQty[j] = atof(vec[11+j*4]);
	}
	ss.OfferNumOrders[0] = atof(vec[52]);
	slashString(vec[54],ss.OfferOrders);
	return true;
	
}

void ifsToMap(string path,unordered_map<int , vector<snapshot>> & m,bool (*readSnapFunc)(string & , snapshot &))
{
	ifstream ifs;
	ifs.open(path.c_str());
	if (!ifs.is_open())	
	{
		cerr<<"Open Error: "<<path.c_str()<<"open failed"<<endl;
		cout<<"Open Error: "<<path.c_str()<<"open failed"<<endl;
	}
	
	//读取txt 跳过第一行 测试只读前5行 &&  rowN < 5
	string  line;
	int rowN = 0;

	while(getline(ifs,line) )
	{
		if(rowN % 1000000 == 0)
			cout << rowN<<endl;
		snapshot ss;
		if ( line.size() > 0 )
		{
			if(readSnapFunc(line,ss))
			{
				auto &v = m[ss.intID];
				if(v.empty()) v.reserve(100000);					
				m[ss.intID].push_back(ss);
			}
			else
			{
				rowN++;
				continue;
			}

		}
		rowN++;
	}
	ifs.close();
	cout<<"ifs close"<<endl;		
	fs::remove(path.c_str());
}


void ifsToMap(std::string &path,unordered_map<int,int>&m)
{
	ifstream ifs;
	ifs.open(path.c_str());
	if (!ifs.is_open())	
	{
		cerr<<"Stickers Open Error: "<<path.c_str()<<"open failed"<<endl;
		cout<<"Open Error: "<<path.c_str()<<"Stickers open failed"<<endl;
	}

	string  line;
	int rowN = 0;

	while(getline(ifs,line) )
	{
		if ( line.size() > 0 )
		{
			
			vector<string> vec = lineToVec(line);
			if(vec[1] != "")
			{
				int tk = atoi(vec[1].c_str());
				m[tk] = (int)(tk/100000);
			}
			
		}
		rowN++;
	}
	ifs.close();
	cout<<"ifs close"<<endl;		

}
