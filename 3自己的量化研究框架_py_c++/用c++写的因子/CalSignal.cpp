#include "stdafx.h"
#include "CalSignal.h"
#include <fstream>
#include <string>
using namespace std;


CalSignal::CalSignal(const std::string &path,const datetime &start,const datetime &end): path(path),start(start),end(end)
{
}


CalSignal& CalSignal::calKline(char sep)
{
	ifstream ifs;
	ifs.open(this->path);
	if(!ifs.is_open())
	{
		throw string("Error:Open Failed");//test ex after throw?
	}
	else
	{
		string line;//如何读取列名获取csv
		int rowN = 0; 
		while (getline(ifs, line))
		{
			if (rowN == 0)
			{
				rowN++;
				continue;
			}
			if (line.size() > 0) 
			{
				vector<char *> vec;
				vec.push_back(&line[0]);
				for (int i = 0;i<line.size();i++)
				{
					if(line[i] == sep)
					{
						line[i] = '\0';
						vec.push_back(&line[i+1]);
					}
				}
				if (datetime(atof(vec[0])) >= start && datetime(atof(vec[0])) <= end)
				{
					this->m_kline[atof(vec[0])] = kline_t(atof(vec[1]), atof(vec[2]), atof(vec[3]),
						atof(vec[4]), atof(vec[5]));

					rowN++;

				}
				
			}
		}
		
	}
	return *this;

}

CalSignal& CalSignal::calSignals()
{
	int klN = 0;
	unsigned int mgN = 0;
	for (auto it = this->m_kline.begin();it != this->m_kline.end();it++)
	{

		//calMerge
		if (klN == 0)
		{
			m_merge[it->first] = merge_t(mgN, it->second.high, it->second.low);
			klN++;
			mgN++;
			continue;
		}
		if (klN == 1)
		{
			m_merge[it->first] = merge_t(mgN, it->second.high, it->second.low);
			klN++;
			mgN++;
			continue;
		}
		auto preMerge1 = --m_merge.end();
		auto preMerge2 = prev(preMerge1,1);
		if ((preMerge1->second.low >= it->second.low && preMerge1->second.high <= it->second.high) ||
			(preMerge1->second.low <= it->second.low && preMerge1->second.high >= it->second.high))
		{
			if (preMerge1->second.high > preMerge2->second.high)
			{
				//向上处理
				m_merge[it->first] = merge_t(mgN, max(it->second.high, preMerge1->second.high),
					max(it->second.low, preMerge1->second.low));
				m_merge.erase(preMerge1);
			}
			else if (preMerge1->second.high < preMerge2->second.high)
			{
				//向下处理
				m_merge[it->first] = merge_t(mgN, min(it->second.high, preMerge1->second.high),
					min(it->second.low, preMerge1->second.low));
				m_merge.erase(preMerge1);
			}
			else
			{
				char err[200];
				sprintf_s(err, "Error:Merge Failed:datetime = %llu", it->first.getVal());
				throw string(err);
			}
		}
		else
		{
			m_merge[it->first] = merge_t(mgN, it->second.high, it->second.low);
			mgN++;
		}
		//calPart & calPen
		calPartPen(it);
		//calPivot
		if (m_pen.size() >= 4)
		{
			calPivot(it);
		}






		//calThreePoint
		klN++;
		
	}
	return *this;

}

void CalSignal::calPartPen(const std::map<datetime, kline_t>::iterator it)
{
	datetime dt = it->first;
	m_merge[dt] = merge_t();
	auto mergeIt = m_merge.find(it->first);
	auto preMerge1 = prev(mergeIt, 1);
	auto preMerge2 = prev(mergeIt, 2);
	if (preMerge1->second.high > max(preMerge2->second.high, mergeIt->second.high)
		&& preMerge1->second.low > max(preMerge2->second.low, mergeIt->second.low))
	{
		if (m_part.size() == 0)
		{
			m_part[dt] = 1;
			m_pen[dt].penD = 1;
			m_pen[dt].penT = 1;
		}
		else
		{
			datetime lastPartDt = (--m_part.end())->first;
			if (mergeIt->second.index - m_merge.find(lastPartDt)->second.index >= 4)
			{
				m_part[dt] = 1;
				if (m_part[lastPartDt] == -1)
				{
					m_pen[dt].penD = 1;
					m_pen[dt].penT = -1;
				}
				else if (m_part[lastPartDt] == 1)
				{
					m_pen[dt].penD = 1;
					m_pen[lastPartDt].penD = 10;
				}
			}
		}
	}
	else if (preMerge1->second.high < min(preMerge2->second.high, mergeIt->second.high)
		&& preMerge1->second.low < min(preMerge2->second.low, mergeIt->second.low))
	{
		if (m_part.size() == 0)
		{
			m_part[dt] = -1;
			m_pen[dt].penD = -1;
			m_pen[dt].penT = -1;
		}
		else
		{
			datetime lastPartDt = (--m_part.end())->first;
			if (mergeIt->second.index - m_merge.find(lastPartDt)->second.index >= 4)
			{
				m_part[dt] = -1;
				if (m_part[lastPartDt] == 1)
				{
					m_pen[dt].penD = -1;
					m_pen[dt].penT = 1;
				}
				else if (m_part[lastPartDt] == -1)
				{
					m_pen[dt].penD = -1;
					m_pen[lastPartDt].penD = -10;
				}
			}
		}

	}

}

void CalSignal::calPivotThreePoint(const std::map<datetime, kline_t>::iterator it)
{
	datetime dt = it->first;
	m_pen[dt] = pen_t();
	auto penIt = m_pen.find(dt);

	if (penIt == m_pen.begin() || penIt->second.penT == DEFAULT_FLOAT) return;
	auto prePen1 = prev(penIt, 1);
	while (prePen1->second.penT == DEFAULT_FLOAT)
	{
		if (prePen1 == m_pen.begin()) return;
		--prePen1;
	}
	auto prePen2 = prev(prePen1, 1);
	while (	prePen2->second.penT == DEFAULT_FLOAT)
	{
		if (prePen2 == m_pen.begin()) return;
		--prePen2;
	}
	auto prePen3 = prev(prePen2, 1);
	while (	prePen3->second.penT == DEFAULT_FLOAT)
	{
		if (prePen3 == m_pen.begin()) break;
		--prePen3;
	}
	auto mergeItD = --m_merge.find(prev(penIt,1)->first);
	auto preMergeD1 = --m_merge.find(prev(prePen1,1)->first);
	auto preMergeD2 = --m_merge.find(prev(prePen2,1)->first);
	auto preMergeD3 = (prePen3 == m_pen.begin()) ? m_merge.find(prev(prePen3,1)->first) : --m_merge.find(prev(prePen3,1)->first);

	if (m_pivot.size() == 0)
	{
		if (prePen3->second.penT == 1)
		{
			float u = min(preMergeD3->second.high, preMergeD1->second.high);
			float d = max(preMergeD2->second.low, mergeItD->second.low);
			if (u > d)
			{
				m_pivot[dt] = pivot_t();
				m_pivot[dt].beginT = prePen3->first;
				m_pivot[dt].endT = dt;
				m_pivot[dt].beginD = prePen3->first; //m_pen.begin(): penD == penT
				m_pivot[dt].endD = prev(penIt, 1)->first;
				m_pivot[dt].type = 1;
				m_pivot[dt].upper = u;
				m_pivot[dt].lower = d;

			}
		}
		else if (prePen3->second.penT == -1)
		{
			float u = min(preMergeD2->second.high, mergeItD->second.high);
			float d = max(preMergeD3->second.low, preMergeD1->second.low);
			if (u > d)
			{
				m_pivot[dt] = pivot_t();
				m_pivot[dt].beginT = prePen3->first;
				m_pivot[dt].endT = dt;
				m_pivot[dt].beginD = prePen3->first; //m_pen.begin(): penD == penT
				m_pivot[dt].endD = prev(penIt, 1)->first;
				m_pivot[dt].type = -1;
				m_pivot[dt].upper = u;
				m_pivot[dt].lower = d;
				m_pivot[dt].isEnd = false;
			}
		}
	}
	else
	{
		if (!(--m_pivot.end())->second.isEnd)
		{
			//之前的中枢尚未结束
			if (penIt->second.penT == 1)
			{
				if (mergeItD->second.high >= (--m_pivot.end())->second.lower)
				{
					//中枢的延伸
					m_pivot[dt] = (--m_pivot.end())->second;
					m_pivot[dt].endD = next(mergeItD, 1)->first;
					m_pivot[dt].endT = dt;
				}
				else
				{
					//三卖定义中枢结束 
					m_threePoint[dt] = 1;
					(--m_pivot.end())->second.isEnd = true;
				}
			}
			else if (penIt->second.penT == -1)
			{
				if (mergeItD->second.low <= (--m_pivot.end())->second.upper)
				{
					//中枢的延伸
					m_pivot[dt] = (--m_pivot.end())->second;
					m_pivot[dt].endD = next(mergeItD, 1)->first;
					m_pivot[dt].endT = dt;
				}
				else
				{
					//三买定义中枢结束 
					m_threePoint[dt] = -1;
					(--m_pivot.end())->second.isEnd = true;
				}

			}

		}
		else 
		{
			//之前的中枢已经结束
			if (prePen3->first >= dt)
			{
				if (prePen3->second.penT == 1)
				{
					float u = min(preMergeD3->second.high, preMergeD1->second.high);
					float d = max(preMergeD2->second.low, mergeItD->second.low);
					if (u > d)
					{
						m_pivot[dt] = pivot_t();
						m_pivot[dt].beginT = prePen3->first;
						m_pivot[dt].endT = dt;
						m_pivot[dt].beginD = prePen3->first; //m_pen.begin(): penD == penT
						m_pivot[dt].endD = prev(penIt, 1)->first;
						m_pivot[dt].type = 1;
						m_pivot[dt].upper = u;
						m_pivot[dt].lower = d;

					}
				}
				else if (prePen3->second.penT == -1)
				{
					float u = min(preMergeD2->second.high, mergeItD->second.high);
					float d = max(preMergeD3->second.low, preMergeD1->second.low);
					if (u > d)
					{
						m_pivot[dt] = pivot_t();
						m_pivot[dt].beginT = prePen3->first;
						m_pivot[dt].endT = dt;
						m_pivot[dt].beginD = prePen3->first; //m_pen.begin(): penD == penT
						m_pivot[dt].endD = prev(penIt, 1)->first;
						m_pivot[dt].type = -1;
						m_pivot[dt].upper = u;
						m_pivot[dt].lower = d;
						m_pivot[dt].isEnd = false;
					}
				}

			}


		}
		

	}

	



	




}





CalSignal::~CalSignal(void)
{
}
