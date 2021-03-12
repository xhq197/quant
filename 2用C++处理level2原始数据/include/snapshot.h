#pragma once
#include <string>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include "utils/time_helper.h"
#include <cfloat>
#include <limits>
using systp = std::chrono::time_point<std::chrono::system_clock>;


struct snapshot
{
	int intID = std :: numeric_limits <int> :: min();
	std::string SecurityID ;
	systp::rep DateTime;
	double PreClosePx = DBL_MIN;
	double OpenPx = DBL_MIN;
	double HighPx = DBL_MIN;
	double LowPx = DBL_MIN;
	double LastPx = DBL_MIN;
	double TotalVolumeTrade = DBL_MIN;
	double TotalValueTrade  = DBL_MIN;
	char InstrumentStatus[100] = {'\0'};
	double BidPrice[10] = {DBL_MIN};
	double BidOrderQty[10] = {DBL_MIN};
	double BidNumOrders[10] = {DBL_MIN};
	double BidOrders[50] = {DBL_MIN};
	double OfferPrice[10] = {DBL_MIN};
	double OfferOrderQty[10] = {DBL_MIN};
	double OfferNumOrders[10] = {DBL_MIN};
	double OfferOrders[50] = {DBL_MIN};
	double NumTrades = DBL_MIN;
	//double IOPV = DBL_MIN;
	double TotalBidQty =DBL_MIN;
	double TotalOfferQty=DBL_MIN;
	double WeightedAvgBidPx = DBL_MIN;
	double WeightedAvgOfferPx = DBL_MIN;
	double TotalBidNumber = DBL_MIN;
	double TotalOfferNumber = DBL_MIN;
	double BidTradeMaxDuration = DBL_MIN;
	double OfferTradeMaxDuration = DBL_MIN;
	double NumBidOrders = DBL_MIN;
	double NumOfferOrders = DBL_MIN;
	double WithdrawBuyNumber = DBL_MIN;
	double WithdrawBuyAmount = DBL_MIN;
	double WithdrawBuyMoney = DBL_MIN;
	double WithdrawSellNumber = DBL_MIN;
	double WithdrawSellAmount = DBL_MIN;
	double WithdrawSellMoney = DBL_MIN;
	/*
	double ETFBuyNumber = DBL_MIN;
	double ETFBuyAmount = DBL_MIN;
	double ETFBuyMoney = DBL_MIN;
	double ETFSellNumber = DBL_MIN;
	double ETFSellAmount = DBL_MIN;
	double ETFSellMoney = DBL_MIN;
	*/
};

bool readSnapshot(std::string &line , struct snapshot &ss);
bool readSnapshotKLBF(std::string &line , snapshot &ss);
void stringToRep(const std::string &word ,systp::rep &l);
void stringToDouble(std::string &word , double &f);
void writeSnapshot(const std::string &date, const std::unordered_map<int , std::vector<struct snapshot>> &m,\
					const std::string &savePath = "/var/L2DB/stk/snap/");
bool readSZBFTable3(std::string &line , struct snapshot &ss); //深交所160509bf + 3、证券行情快照数据
bool readSZBFTable4(std::string &line , struct snapshot &ss); //深交所160509bf + 4、证券委托队列数据
std::string changeStrLen(int tarTen ,const std::string &initString);
std::vector<std::string> lineToVec(std::string &line,const char &sep = ',');
void lineToCharStarVec(std::string &line,std::vector<char *> &vec ,const char &sep = ',');
void slashString(const std::string &str,double arr[],std::string sep = "|",unsigned int slashIndex0 =0,int i = 0);
bool readSZAFTableHq(std::string &line , struct snapshot &ss); //深交所160509af + 现货证券行情快照表hq_snap_spot.txt 
bool readSZAFTableLevel(std::string &line , struct snapshot &ss); //深交所160509af + 现货证券行情快照档位表snap_level_spot.txt
void ifsToMap(std::string path,std::unordered_map<int , std::vector<struct snapshot>> & m,\
					bool (*writeSnapFunc)(std::string & , struct snapshot &));
void ifsToMap(std::string &tkNamePAth,std::unordered_map<int,int>&m); 


