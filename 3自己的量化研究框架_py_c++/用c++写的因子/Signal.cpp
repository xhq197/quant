#include "stdafx.h"
#include "Signal.h"

kline_t::kline_t(float open, float high, float low, float close, float vol):open(open),close(close),high(high),low(low),vol(vol)
{

}

kline_t::kline_t():open(DEFAULT_FLOAT),close(DEFAULT_FLOAT),high(DEFAULT_FLOAT),low(DEFAULT_FLOAT),vol(DEFAULT_FLOAT)
{
}



pivot_t::pivot_t():beginT(DEFAULT_TIME),endT(DEFAULT_TIME),beginD(DEFAULT_TIME),endD(DEFAULT_TIME)
, upper(DEFAULT_FLOAT),lower(DEFAULT_FLOAT),type(DEFAULT_FLOAT),isEnd(false)
{
}



merge_t::merge_t() : index(DEFAULT_U), high(DEFAULT_FLOAT),low(DEFAULT_FLOAT)
{
}

merge_t::merge_t(unsigned int index,float high, float low): index(DEFAULT_U), high(high),low(low)
{
}

pen_t::pen_t():penD(DEFAULT_FLOAT),penT(DEFAULT_FLOAT)
{
}

pen_t::pen_t(float penD, float penT): penD(penD),penT(penT)
{
}
