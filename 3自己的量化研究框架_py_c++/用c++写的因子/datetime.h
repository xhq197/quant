#pragma once
#include <string>

class datetime {
public:
	datetime(const unsigned long long value);
	datetime(const std::string strTime);//strTime 格式必须为"2019-01-02 10:30:00"
	unsigned long long getVal() const;
	//int getYear() const;
	//int getMonth() const;
	//int getDay() const;
	//int getHour() const;
	//int getMinute() const;
	//int getSecond() const;
	bool operator<(const datetime &d2) const;
	bool operator>(const datetime &d2) const;
	bool operator<=(const datetime &d2) const;
	bool operator>=(const datetime &d2) const;
private:
	unsigned long long value;

};