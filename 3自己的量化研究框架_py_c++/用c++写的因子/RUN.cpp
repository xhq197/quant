// dissertation.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "CalSignal.h"
#include "Signal.h"
#include "datetime.h"
#include <cstdlib>
#include <iostream>
using namespace std;



int _tmain(int argc, _TCHAR* argv[])
{
	
	//CalSignal c("", 000000, 2000000);
	//datetime d("2019-01-02 10:30:11");
	map<int, int> m{{1,11},{2,22}};
	prev(m.begin(), 1);
	system("pause");
	return 0;
}

