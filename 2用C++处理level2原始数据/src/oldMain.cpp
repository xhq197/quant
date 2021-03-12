#include "utils/time_helper.h"
#include "utils/trace_info.h"

using namespace std;
using namespace qts;

const char progname[] = "l2dmgr";

#define MD_DEPTH 10

/** <summary>深度行情.</summary> */
struct MarketData
{
    /// <summary>申买价.</summary>      
    double BidPrice[MD_DEPTH];
    /// <summary>申卖价.</summary>
    double AskPrice[MD_DEPTH];
    /// <summary>申买量.</summary>
    int    BidVolume[MD_DEPTH];
    /// <summary>申卖价一.</summary>
    int    AskVolume[MD_DEPTH];
    /// <summary>数量.</summary>
    int	Volume;
    /// <summary>最新价.</summary>
    double	LastPrice;
    /// <summary>成交金额.</summary>
    double	Turnover;
    /// <summary>当日均价.</summary>
    double AveragePrice;
    /// <summary>持仓量.</summary>
    double	OpenInterest;
    /// <summary>合约代码.</summary>
    char InstrumentID[Len_InstrumentID];
    /// <summary>the time point of updating</summary>
    std::chrono::time_point<std::chrono::system_clock>::rep UpdateTime;
    ExchangeEnum TradingExchange;
    /// <summary>上次结算价.</summary>
    double	PreSettlementPrice;
    /// <summary>本次结算价.</summary>
    double SettlementPrice;
    /// <summary>昨收盘.</summary>
    double	PreClosePrice;
    /// <summary>今开盘.</summary>
    double	OpenPrice;
    /// <summary>今最高价.</summary>
    double	HighestPrice;
    /// <summary>今最低价.</summary>
    double	LowestPrice;
    /// <summary>今收盘价.</summary>
    double ClosePrice;
    /// <summary>申买价一.</summary>
    /// <summary> The upper limit price. </summary>
    double UpperLimitPrice;
    /// <summary> The lower limit price. </summary>
    double LowerLimitPrice;
    std::chrono::time_point<std::chrono::system_clock>::rep ReceivedTime;
};
typedef MarketData MD;

/*
int main()
{
    vector<MD> v;
    v.resize(1000);

    auto p = (char*)(&v[0]);
    auto N = sizeof(MD) * v.size();

    utils::trace_info(progname, "{} done. now: {}", __func__, utils::toString(utils::systp::clock::now()));
}

*/