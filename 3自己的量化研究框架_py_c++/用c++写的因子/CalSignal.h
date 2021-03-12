#pragma once
#include <string>
#include "Signal.h"
#include "datetime.h"
#include <map>
class CalSignal
{
public:
	CalSignal(const std::string &path,const datetime &start,const datetime &end);

	//�����kline.csv��kline.txt������ѭdatetime��open��high��low��vol˳��datetime��ʽΪyyyymmddHHMMSS
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
	std::map<datetime, float> m_threePoint; //������㣺-1 ������㣺1 �߼����������
	void calPartPen(const std::map<datetime, kline_t>::iterator it);
	void calPivotThreePoint(const std::map<datetime, kline_t>::iterator it);
};

