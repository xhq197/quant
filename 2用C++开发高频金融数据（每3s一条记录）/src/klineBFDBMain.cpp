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
	string tempPath = "/home/xiehq/dmgrl2/temp/KLBF/SH/";
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
		writeSnapshot(date, m,"/var/L2DB/stk/klineBF/SH/");
		endTime = clock();//计时结束
		cout << "The run time is(SH one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cout<<"The number of compressed stocks(SH) :"<<m.size()<<endl;
		cerr<<"The run time is(SH one day): " <<(double)(endTime - startTime) / CLOCKS_PER_SEC << "s" << endl;
		cerr<<"The number of compressed stocks(SH) :"<<m.size()<<endl;
		cout<<"##########"<<*it<<"--SH END"<<"##########"<<endl;
	}
	utils::trace_info(progname, "{} done. now: {}", __func__, utils::toString(utils::systp::clock::now()));
}
