#include "zlib.h"
#include <string>
#include <exception>
#include <string>
#include <chrono>
#include <algorithm>
#include <sstream>
#include <cstring>
#include <atomic>
#include <thread>
#include <cfloat>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <cassert>
#include <cstdio>

namespace qts{ namespace utils{

std::string uncompressread(FILE *source, const size_t CHUNKIN);

bool compresswrite(const std::string & fileName, const char* str, size_t N);

}}