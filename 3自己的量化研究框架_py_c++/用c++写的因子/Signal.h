#pragma once
#include <map>
#include <unordered_map>
#include <string>
#include "datetime.h"
#define DEFAULT_TIME datetime("1990-00-00 00:00:00")
#define DEFAULT_FLOAT FLT_MIN
#define DEFAULT_U 0
struct kline_t
{
	kline_t();
	kline_t(float open, float high, float low, float close, float vol);
	float open, high, low, close, vol;
};



struct pivot_t
{
	pivot_t();
	datetime beginT;//pivot 确立开始的时间
	datetime endT;//pivot 确立结束的时间
	datetime beginD; //pivot绘图块的开始
	datetime endD;//pivot绘图块的结束
	float upper;
	float lower;
	float type; //1:向上形成的中枢 -1：向下形成的中枢
	bool isEnd;
};

struct merge_t
{
	merge_t();
	merge_t(unsigned int index,float high, float low);
	unsigned long long  index; //merge的index
	float high, low;
};

struct pen_t
{
	pen_t();
	pen_t(float penD, float penT);
	float penD, penT;//绘图使用penD，确立使用penT
};



