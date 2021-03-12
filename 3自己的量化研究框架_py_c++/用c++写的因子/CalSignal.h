#pragma once
#include <string>
#include "Signal.h"
#include "datetime.h"
#include <map>
class CalSignal
{
public:
	CalSignal(const std::string &path,const datetime &start,const datetime &end);

	//输入的kline.csv或kline.txt必须遵循datetime，open，high，low，vol顺序，datetime格式为yyyymmddHHMMSS
	CalSignal& calKline(char sep = ',');
	CalSignal& calSignals();


	~CalSignal(void);
private:
	const std::string path;
	const datetime start,end;
	std::map<datetime,kline_t> m_kline;
	//std::map<datetime,signals> m_signals;
	std::map<datetime, merge_t> m_merge;
	std::map<datetime, pivot_t> m_pivot;
	std::map<datetime, float> m_part;
	std::map<datetime, pen_t> m_pen;
	std::map<datetime, float> m_threePoint; //第三买点：-1 第三买点：1 逻辑：低买高卖
	void calPartPen(const std::map<datetime, kline_t>::iterator it);
	void calPivotThreePoint(const std::map<datetime, kline_t>::iterator it);
};

