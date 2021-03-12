#include <vector>
#include <map>
#include <string>
#include "utils/time_helper.h"
using systp = std::chrono::time_point<std::chrono::system_clock>;


struct tick
{
    int intID = 0;
    std::string Symbol = "NULL";
    systp::rep TradingTime = qts::utils::systp2rep(qts::utils::to_time_point("199410011200.000"));
    double PreClosePrice = 0;
    double OpenPrice = 0;
    double HighPrice = 0;
    double LowPrice = 0;
    double LastPrice = 0;
    double TotalVolume = 0;
    double TotalAmount = 0;
    double TotalNo = 0;
    double DoubleTime = 0;
    double SellVolumeSum = 0;
    double BuyVolumeSum = 0;
    double DoubleTemp = 0;
};


bool readTickCsv(std::string &line , struct tick &tk);
bool readTickCsvBF(std::string &line , struct tick &tk);
std::string tarTimeString(std::string &timeStr);// 2020-11-10 09:25:00.000 -> 20201110092500.000
void getKlineRep(int minN,std::string date,std::vector<systp::rep> &vec);
void getKlineTimeStr(int minN,std::string date,std::vector<std::string> &vec);
void getKlineBFTimeStr(int minN,std::string date,std::vector<std::string> &vec);

double stringToDouble(std::string &word);
std::string intToString2p(int i);
std::string intToString(int i);
//获取每天(minN) min Kline的时间戳，取每段时间的末时刻作为时间戳 return ： (20201110092500.000->rep)

struct kline
{
    std::string StockID = "NULL";
    std::string StockName = "NULL"; 
    systp::rep sepDateTime = qts::utils::systp2rep(qts::utils::to_time_point("199410011200.000")); //20201110092500.000->rep
    double price = 0; //收盘价
    double open = 0;
    double high = 0;
    double low = 0;
    double vol = 0;
    double askVol = 0;
    double bidVol = 0;
    double amount = 0;
    double cjbs = 0; //成交笔数
    double yclose = 0; //昨收价
    std::string Time = "NULL"; //09:25:00 //rep_to_string 或者 只取时分秒的函数在哪?????
    std::string Expr1 = "NULL";

    kline operator=(kline& klTmp)
    {
        // StockID = klTmp.StockID;
        // StockName = klTmp.StockName;
        // sepDateTime = klTmp.sepDateTime;
        price = klTmp.price;
        open = klTmp.open;
        high = klTmp.high;
        low = klTmp.low;
        vol = klTmp.vol;
        askVol = klTmp.askVol;
        bidVol = klTmp.bidVol;
        // amount = klTmp.amount;
        // cjbs = klTmp.cjbs;
        // yclose = klTmp.yclose;
        // Time = klTmp.Time;
        // Expr1 = klTmp.Expr1;
        return *this;
    };

};
