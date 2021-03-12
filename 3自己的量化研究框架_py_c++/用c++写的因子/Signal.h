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
	datetime beginT;//pivot ȷ����ʼ��ʱ��
	datetime endT;//pivot ȷ��������ʱ��
	datetime beginD; //pivot��ͼ��Ŀ�ʼ
	datetime endD;//pivot��ͼ��Ľ���
	float upper;
	float lower;
	float type; //1:�����γɵ����� -1�������γɵ�����
	bool isEnd;
};

struct merge_t
{
	merge_t();
	merge_t(unsigned int index,float high, float low);
	unsigned long long  index; //merge��index
	float high, low;
};

struct pen_t
{
	pen_t();
	pen_t(float penD, float penT);
	float penD, penT;//��ͼʹ��penD��ȷ��ʹ��penT
};



