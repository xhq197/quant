#include "stdafx.h"
#include "datetime.h"
#include <iostream>
using namespace std;

datetime::datetime(const unsigned long long value):value(value)
{
}

datetime::datetime(const std::string strTime)
{
	int pos1 = strTime.find('-');
	int pos2 = strTime.find('-',pos1 +1);
	int pos3 = strTime.find(' ',pos2+1);
	int pos4 = strTime.find(':',pos3+1);
	int pos5 = strTime.find(':',pos4+1);
	this->value = atof(strTime.substr(0,pos1).c_str())*1e10 
		+ atof(strTime.substr(pos1+1,pos2 - pos1 -1).c_str())*1e8 
		+atof(strTime.substr(pos2+1,pos3 - pos2 -1).c_str())*1e6 
		+atof(strTime.substr(pos3+1,pos4 - pos3 -1).c_str())*1e4
		+atof(strTime.substr(pos4+1,pos5 - pos4 -1).c_str())*1e2
		+atof(strTime.substr(pos5+1,2).c_str());
}

unsigned long long datetime::getVal() const
{
	return this->value;
}

//map的key必须有<操作符
bool datetime::operator<(const datetime &d2) const
{
	return this->value < d2.value;
}

bool datetime::operator<=(const datetime &d2) const
{
	return this->value <= d2.value;
}

bool datetime::operator>=(const datetime &d2) const
{
	return this->value >= d2.value;
}

bool datetime::operator>(const datetime &d2) const
{
	return this->value > d2.value;
}
