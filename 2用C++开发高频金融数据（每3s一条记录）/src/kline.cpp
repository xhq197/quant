#include "kline.h"
#include "snapshot.h"
#include <vector>
using namespace std;
#include <sstream>
#include <iostream>
ofstream klineBFErr;


bool readTickCsv(std::string &line , struct tick &tk)
{
    vector<string> vec = lineToVec(line);
    if(vec.size() >= 104 && vec.size() <=106)
    {
	tk.Symbol  = changeStrLen(6,vec[0]); 
    string tarT= tarTimeString(vec[2]);
    tk.DoubleTime = stringToDouble(tarT);
    stringToRep( tarT,tk.TradingTime); 
    stringToDouble(vec[3],tk.PreClosePrice);
    stringToDouble(vec[4],tk.OpenPrice);
    stringToDouble(vec[5],tk.HighPrice);
    stringToDouble(vec[6],tk.LowPrice);
    stringToDouble(vec[7],tk.LastPrice);
    stringToDouble(vec[52],tk.TotalVolume);
    stringToDouble(vec[53],tk.TotalAmount);
    stringToDouble(vec[51],tk.TotalNo);
    return true;
    }
    else klineBFErr<<"Raw Data Columns Error:this line("<<changeStrLen(6,vec[0])<<"_"<<vec[2]<<") does not contain enough columns(104 cols) "<<endl;
    return false;
}

bool readTickCsvBF(std::string &line , struct tick &tk)
{
    vector<string> vec = lineToVec(line);
    int tpS = vec.size();
    if(vec.size() < 104 || vec.size() >106) ///????
    {
        if(tpS >= 3) klineBFErr<<"Columns Error: 104/106!="<<tpS<<"--"<<vec[0]<<"-"<<vec[2]<<endl;
        else klineBFErr<<"Columns Error: 104/106!="<<tpS<<endl;
        return false;
    }

	tk.Symbol  = changeStrLen(6,vec[0]); 
    string tarT= tarTimeString(vec[2]);
    tk.DoubleTime = atof(tarT.c_str());
    stringToRep( tarT,tk.TradingTime); 
    tk.PreClosePrice = atof(vec[3].c_str());
    tk.LastPrice = (atof(vec[19].c_str()) +atof(vec[20].c_str()))/2;
    tk.DoubleTemp = atof(vec[7].c_str());
    tk.OpenPrice = tk.LastPrice;
    tk.HighPrice = tk.LastPrice;
    tk.LowPrice = tk.LastPrice;
    for(int j = 0;j<1;j++)
    {
        tk.BuyVolumeSum += atof(vec[41+j].c_str());
        tk.SellVolumeSum += atof(vec[40-j].c_str());
    }
    return true;
}

    
std::string tarTimeString(std::string &timeStr)
{
    string mode = "2020-11-10 09:25:00.000";
    if(timeStr.length() == mode.length())
    return timeStr.substr(0,4) + timeStr.substr(5,2) + timeStr.substr(8,2) + timeStr.substr(11,2) + \
    timeStr.substr(14,2) + timeStr.substr(17);
    else return "19491001120000.000";
}


void getKlineRep(int minN,std::string date,std::vector<systp::rep> &vec)
{   
    string time;
    systp::rep repTime;
    int s = 0;
    cout<<"AM******"<<endl;
    for(int h = 9;h <= 11 ;h++)
    {
        for(int m = 0;m<= 59;m+=minN)
        {  
            
            if(h == 9 && m < 30) continue; 
            if(h == 11 && m > 30) continue;
            time = date+intToString2p(h) + intToString2p(m) +intToString2p(s)+".000";
            cout << intToString2p(h) + intToString2p(m) +intToString2p(s) <<"--";
            stringToRep(time,repTime);
            vec.push_back(repTime);
            
        }
    }
    cout<<endl<<"PM******"<<endl;
    for(int h = 13;h < 15 ;h++)
    {
        for(int m = 0;m< 60;m+=minN)
        {  
            time = date+intToString2p(h) + intToString2p(m) +intToString2p(s)+".000";
            cout << intToString2p(h) + intToString2p(m) +intToString2p(s) <<"--";
            stringToRep(time,repTime);
            vec.push_back(repTime);
        
        }
    }
    time = date+intToString2p(15) + intToString2p(0) +intToString2p(0)+".000";
    cout << intToString2p(15) + intToString2p(0) +intToString2p(0) <<endl;
    stringToRep(time,repTime);
    vec.push_back(repTime);
    
}


void getKlineTimeStr(int minN,std::string date,std::vector<std::string> &vec)
{   
    string time;
    int s = 0;
    cout<<"AM******"<<endl;
    for(int h = 9;h <= 11 ;h++)
    {
        for(int m = 0;m<= 59;m+=minN)
        {  
            
            if(h == 9 && m <= 30) continue; 
            if(h == 11 && m > 30) continue;
            time = date+intToString2p(h) + intToString2p(m) +intToString2p(s)+".000";
            cout << intToString2p(h) + intToString2p(m) +intToString2p(s) <<"--";
            vec.push_back(time);
            
        }
    }
    cout<<endl<<"PM******"<<endl;
    for(int h = 13;h < 15 ;h++)
    {
        for(int m = 0;m< 60;m+=minN)

        {   if(h == 13 && m == 0 ) continue; 
            time = date+intToString2p(h) + intToString2p(m) +intToString2p(s)+".000";
            cout << intToString2p(h) + intToString2p(m) +intToString2p(s) <<"--";
            vec.push_back(time);
        
        }
    }
    time = date+intToString2p(15) + intToString2p(0) +intToString2p(0)+".000";
    cout << intToString2p(15) + intToString2p(0) +intToString2p(0) <<endl;
    vec.push_back(time);
    
}


void getKlineBFTimeStr(int minN,std::string date,std::vector<std::string> &vec)
{
    string time;
    int s = 0;
    cout<<"AM******"<<endl;
    for(int h = 9;h <= 9 ;h++)
    {
        for(int m = 15;m<= 25;m+=minN)
        {  
            
            time = date+intToString2p(h) + intToString2p(m) +intToString2p(s)+".000";
            cout << intToString2p(h) + intToString2p(m) +intToString2p(s) <<"--";
            vec.push_back(time);
            
        }
    }
}

string intToString2p(int i)
{   
    char ss[100];
    sprintf(ss,"%d",i);
    string s(ss);
    if(i<10) return "0" + s; else return s;
}

string intToString(int i)
{   
    char ss[100];
    sprintf(ss,"%d",i);
    string s(ss);
    return s;
}



// string intToString2p(int i)
// {   string s;
//     stringstream ss;
//     ss << i;
//     ss >> s;
//     if(i<10) return "0" + s; else return s;
// }

// string intToString(int i)
// {   string s;
//     stringstream ss;
//     ss << i;
//     ss >> s;
//     return s;
// }


double stringToDouble(std::string &word)
{
    return atof(word.c_str());
}