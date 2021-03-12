#include <fstream>
#include <iostream>
#include <cstdlib>
#include "snapshot.h"
#include "compress.h"
#include "listFiles.h"
#include "utils/trace_info.h"
#include <iomanip>
#include <cstdio>
#include <unordered_map> //#include <unordered_map>
#include <vector>
#include <filesystem>
using namespace std;
using namespace qts;
using namespace qts::utils;
namespace fs = std::filesystem;
const char progname[] = "l2dmgr";
#include "kline.h"
#include<ctime>
extern  ofstream ofsErr;
extern unordered_map<int,int> tkMap;
#include <pthread.h>

/////////////上交所/////////////	

void mainSH(string errPath)
{
	ofsErr.open(errPath);
	cerr.rdbuf(ofsErr.rdbuf()); 
	std::string path = "/mnt/data_backup/L2SH/2020/";
	string tempPath = "/home/xiehq/dmgrl2/temp/SH/";
	std::vector<std::string> files;
	getFiles(path, files);
	string csvName = "Snapshot";
	//测试只读2020年9月21日 -2020年10月21日
	// auto tempIt = files.begin();
	// for(int num =0;num<2;num++) tempIt++;	
	for (auto it = files.begin();it!=files.end();it++){
		clock_t startTime,endTime;
		startTime = clock();//计时开始
		string tempStr = it->substr(it->length()-8);
		if(atof(tempStr.c_str()) < 20200921) continue;
		string unzipStr = "7za e " + (*it) +"/Snapshot.7z.001 -o"+tempPath;
		if(system(unzipStr.c_str()) == -1)
		{
			cout <<"Unzip Error: SH unzip faild"<<endl;
			cerr <<"Unzip Error: SH unzip faild"<<endl;
		} 
		cout<<"***********"<<*it<<"--SH BFGIN"<<"***********"<<endl;
		string date = it->substr(it->rfind('/')+1);
		string oldName = tempPath + csvName + ".csv";
		string newName = tempPath + csvName + date + ".csv";
		fs::rename(oldName,newName);
		unordered_map<int , vector<snapshot>> m; //unordered_map
		m.reserve(4000);
		ifsToMap(newName,m,readSnapshot); 
		cout<<"write--SH"<<date<<endl;
		writeSnapshot(date, m,"/var/L2DB/stk/snapSH/");
		endTime = clock();//计时结束
		cout << "The run time is(SH one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cout<<"The number of compressed stocks(SH) :"<<m.size()<<endl;
		cerr<<"The run time is(SH one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cerr<<"The number of compressed stocks(SH) :"<<m.size()<<endl;
		cout<<"##########"<<*it<<"--SH END"<<"##########"<<endl;
	}
	utils::trace_info(progname, "{} done. now: {}", __func__, utils::toString(utils::systp::clock::now()));
}



/////////////深交所20160509BF/////////////
void mainSZBF(string errPath)
{
	ofsErr.open(errPath);
	cerr.rdbuf(ofsErr.rdbuf()); 
	string path = "/mnt/data_backup/L2SZ/2016/";
	string tempPath = "/home/xiehq/dmgrl2/temp/SZ/BF/";
	std::vector<std::string> files;
	getFiles(path, files,false);
	//测试只读files前5个迭代器
	// auto tempIt = files.begin();
	// for(int num =0;num<5;num++) tempIt++;	
	for (auto it = files.begin();it!=files.end();it++)
	{
		clock_t startTime,endTime;
		startTime = clock();//计时开始
		int pathLen = path.length();
		if(it->find('/',pathLen) == (int)string::npos) continue;

		string date = it->substr(22,4) +it->substr(27,2) +it->substr(30);  //假设目录恒为 /YYYY/MM/DD/
		if(atof(date.c_str()) > 20160501 || atof(date.c_str()) < 20160401 ) continue;
		cout<<"***********"<<*it<<"--SZBF BFGIN"<<"***********"<<endl;
		cout << "date:"<<date <<endl;
		unordered_map<int , vector<snapshot>> m;
		m.reserve(4000);
		{
		////table 3:SNAPSHOT
		string unzipStr = "7za e " + (*it) +"/SZL2_SNAPSHOT_"+ date +".7z.001 -o"+tempPath; //SZL2_SNAPSHOT_20140102.7z.001
		if(system(unzipStr.c_str()) == -1) 
		{
			cout <<"Unzip Error: SZBF_SNAPSHOT_table3 unzip faild"<<endl;
			cerr <<"Unzip Error: SZBF_SNAPSHOT_table3 unzip faild"<<endl;
		}
		
		string txtPath = tempPath ; 
		string amTxtPath = txtPath+"SZL2_SNAPSHOT_" +date+ "_AM.txt";
		string pmTxtPath = txtPath+"SZL2_SNAPSHOT_" +date+ "_PM.txt";
		// SZL2_SNAPSHOT_20140102/SZL2_SNAPSHOT_20140102_AM.txt 和  SZL2_SNAPSHOT_20140102/SZL2_SNAPSHOT_20140102_PM.txt
		vector<string> txtVec = {amTxtPath,pmTxtPath};
		for(auto txtIt = txtVec.begin();txtIt!= txtVec.end();txtIt++) ifsToMap(*txtIt,m,readSZBFTable3); 
		}
		{
		////table4 : SNAPSHOTDW
		string unzipStr = "7za e " + (*it) +"/SZL2_SNAPSHOTDW_"+ date +".7z.001 -o"+tempPath; //SZL2_SNAPSHOTDW_20140102.7z.001
		if(system(unzipStr.c_str()) == -1) 
		{
			cout <<"Unzip Error: SZBF_SNAPSHOTDW_table4 unzip faild"<<endl;
			cerr <<"Unzip Error: SZBF_SNAPSHOTDW_table4 unzip faild"<<endl;
		}
		string txtPath = tempPath ; 
		string amTxtPath = txtPath+"SZL2_SNAPSHOTDW_" +date+ "_AM.txt";
		string pmTxtPath = txtPath+"SZL2_SNAPSHOTDW_" +date+ "_PM.txt";
		// SZL2_SNAPSHOTDW_20140102/SZL2_SNAPSHOTDW_20140102_AM.txt 和  SZL2_SNAPSHOTDW_20140102/SZL2_SNAPSHOTDW_20140102_PM.txt
		vector<string> txtVec = {amTxtPath,pmTxtPath};
		for(auto txtIt = txtVec.begin();txtIt!= txtVec.end();txtIt++) ifsToMap(*txtIt,m,readSZBFTable4); 
		}
		//写入
		cout<<"write--SZBF"<<date<<endl;
		writeSnapshot(date, m,"/var/L2DB/stk/snapSZBF/");
		endTime = clock();//计时结束
		cout << "The run time is(SZBF one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cout<<"The number of compressed stocks(SZBF) :"<<m.size()<<endl;
		cerr<< "The run time is(SZBF one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cerr<<"The number of compressed stocks(SZBF) :"<<m.size()<<endl;
		cout<<"##########"<<*it<<"--SZBF END"<<"##########"<<endl;
		
		utils::trace_info(progname, "{} done. now: {}", __func__, utils::toString(utils::systp::clock::now()));

	}

}

/////////////深交所20160509AF/////////////
void  mainSZAF(string errPath)
{
	ofsErr.open(errPath);
	cerr.rdbuf(ofsErr.rdbuf()); 
	string path = "/mnt/data_backup/L2SZ/2020/";
	string tempPath = "/home/xiehq/dmgrl2/temp/SZ/AF/";
	std::vector<std::string> files;
	getFiles(path, files);
	//测试只读files前5个迭代器
	// auto tempIt = files.begin();
	// for(int num =0;num<5;num++) tempIt++;	
	
	for (auto it = files.begin();it!=files.end();it++)
	{
		clock_t startTime,endTime;
		startTime = clock();//计时开始
		int pathLen = path.length();
		if((it->length() - path.length()) <= 3) continue;

		string date = it->substr(22,4) +it->substr(27);  //假设目录恒为 /YYYY/MM/DD/
		if(atof(date.c_str()) < 20200921  ) continue;
		cout<<"***********"<<*it<<"--SZAF BFGIN"<<"***********"<<endl;
		cout << "date:"<<date <<endl;
		unordered_map<int , vector<snapshot>> m;
		m.reserve(4000);
		{
		////table 1:hq_snap_spot.txt 
		string mkdir = tempPath + "hq_snap_spot" + date ;
		if(!fs::exists(mkdir)) fs::create_directories(mkdir);
		string txtPath = mkdir+"/" ; 
		string unzipStr = "7za e " + (*it) +"/am_hq_snap_spot.7z.001 -o"+txtPath; //am_hq_snap_spot.7z.001
		if(system(unzipStr.c_str()) == -1)
		{
			cout <<"Unzip Error: SZAF_am_hq unzip faild"<<endl;
			cerr <<"Unzip Error: SZAF_am_hq unzip faild"<<endl;
		} 
		unzipStr = "7za e " + (*it) +"/pm_hq_snap_spot.7z.001 -o"+txtPath; //pm_hq_snap_spot.7z.7z.001
		if(system(unzipStr.c_str()) == -1)
		{
			cout <<"Unzip Error: SZAF_pm_hq unzip faild"<<endl;
			cerr <<"Unzip Error: SZAF_pm_hq unzip faild"<<endl;
		} 
		string amTxtPath = txtPath+"am_hq_snap_spot.txt";//am_hq_snap_spot.txt
		string pmTxtPath = txtPath+"pm_hq_snap_spot.txt"; //pm_hq_snap_spot.txt
		vector<string> txtVec = {amTxtPath,pmTxtPath};
		for(auto txtIt = txtVec.begin();txtIt!= txtVec.end();txtIt++) 
		{
			cout<<*txtIt<<"--into"<<endl;
			ifsToMap(*txtIt,m,readSZAFTableHq); 
		}
		fs::remove_all(txtPath.c_str());
		}

		{
		////table2 :  snap_level_spot.txt
		string mkdir = tempPath + "snap_level_spot" + date ;
		if(!fs::exists(mkdir)) fs::create_directories(mkdir);
		string txtPath = mkdir+"/" ; 
		string unzipStr = "7za e " + (*it) +"/am_snap_level_spot.7z.001 -o"+txtPath; //am_snap_level_spot.7z.001
		if(system(unzipStr.c_str()) == -1) 
		{
			cout <<"Unzip Error: SZAF_am_level unzip faild"<<endl;
			cerr <<"Unzip Error: SZAF_am_level unzip faild"<<endl;
		}
		unzipStr = "7za e " + (*it) +"/pm_snap_level_spot.7z.001 -o"+txtPath; //pm_snap_level_spot.7z.001
		if(system(unzipStr.c_str()) == -1) 
		{
			cout <<"Unzip Error: SZAF_pm_level unzip faild"<<endl;
			cerr <<"Unzip Error: SZAF_pm_level unzip faild"<<endl;
		}
		string amTxtPath = txtPath+"am_snap_level_spot.txt";//am_snap_level_spot.txt
		string pmTxtPath = txtPath+"pm_snap_level_spot.txt"; //pm_snap_level_spot.txt
		vector<string> txtVec = {amTxtPath,pmTxtPath};
		for(auto txtIt = txtVec.begin();txtIt!= txtVec.end();txtIt++)
		{
			cout<<*txtIt<<"--into"<<endl;
			ifsToMap(*txtIt,m,readSZAFTableLevel);
		} 
		fs::remove_all(txtPath.c_str());
		}
		//检验
		// auto mit = m.begin();
		// cout<<(mit->first)<<"--"<<mit->second[0].intID<<endl;
		//写入
		cout<<"write--SZAF"<<date<<endl;
		writeSnapshot(date, m,"/var/L2DB/stk/snapSZAF/");
		endTime = clock();//计时结束
		cout << "The run time is(SZAF one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cout<<"The number of compressed stocks(SZAF) :"<<m.size()<<endl;
		cerr<<"The run time is(SZAF one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cerr<<"The number of compressed stocks(SZAF) :"<<m.size()<<endl;
		cout<<"##########"<<*it<<"--SZAF END"<<"##########"<<endl;
		
		utils::trace_info(progname, "{} done. now: {}", __func__, utils::toString(utils::systp::clock::now()));

	}
	

}
	


int main()
{
	// string line = "12,3664,546,789";
	// vector<char *> vec;

	// lineToCharStarVec(line,vec);
	// cout<<vec[0]<<endl;
	// cout<<atof(vec[1])<<endl;
	// cout<<atof(vec[2])<<endl;
	// cout<<atof(vec[3])<<endl;
	
	

	// string tkNamePAth = "/var/TSDB/stk/tickers.csv";
	// ifsToMap(tkNamePAth,tkMap); 
	// string errSZAFPath = "/home/xiehq/dmgrl2/temp/errorSZAF.txt";
	// mainSZAF(errSZAFPath); 
	// string errSZBFPath = "/home/xiehq/dmgrl2/temp/errorSZBF.txt";
	// mainSZBF(errSZBFPath);
	// string errSZAFPath = "/home/xiehq/dmgrl2/temp/errorSZAF.txt";
	// mainSZAF(errSZAFPath); 

	// thread t0([]()
	// {
	// 	cout<<"运行线程--SH"<<endl;
	// 	string errSHPath = "/home/xiehq/dmgrl2/temp/errorSH.txt";
	// 	mainSH(errSHPath);
	// }); 
	// thread t1([]()
	// {
	// 	cout<<"运行线程--SZBF"<<endl;
	// 	string errSZBFPath = "/home/xiehq/dmgrl2/temp/errorSZBF.txt";
	// 	mainSZBF(errSZBFPath);
	// }); 
	// thread t2([]()
	// {
	// 	cout<<"运行线程--SZAF"<<endl;
	// 	// string tkNamePAth = "/var/TSDB/stk/tickers.csv";
	// 	// ifsToMap(tkNamePAth,tkMap); 
	// 	string errSZAFPath = "/home/xiehq/dmgrl2/temp/errorSZAF.txt";
	// 	mainSZAF(errSZAFPath); 
	// });
	// t0.join();
	// t1.join();
	// t2.join();
	
	fs::remove_all("/var/L2DB/stk/snapSH/");
	fs::remove_all("/var/L2DB/stk/snapSZAF/");
	fs::remove_all("/var/L2DB/stk/snapSZBF/");
	cout<<"$$$$$$$$$$$$$$ ALELE $$$$$$$$$$$$$$$$$"<<endl;
	return 0;
}

// int main()
// {	ifstream ifs;
// 	string path = "/home/xiehq/dmgrl2/temp/test.txt";	
// 	std::vector<char *> vec;
// 	ifs.open(path);
// 	if (!ifs.is_open())	
// 	{
// 		cerr<<"Open Error: "<<path<<"open failed"<<endl;
// 		cout<<"Open Error: "<<path<<"open failed"<<endl;
// 	}
	
// 	//读取txt 跳过第一行 测试只读前5行 &&  rowN < 5
// 	string  line;
// 	int rowN = 0;

// 	while(getline(ifs,line) && rowN >0)
// 	{
// 		lineToCharStarVec(line,vec,'\t');
// 	}
// 	ifs.close();
// 	cout<<"ifs close"<<endl;	

	
	
// 	return 0;
// }

















