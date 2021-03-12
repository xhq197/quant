#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <cstddef>
#include <string>
#include <vector>
#include <cstring>
#include <iostream>
void getFiles(const std::string path, std::vector<std::string> &files,bool getFolder = true);
//？？？对比true false
void getFiles1Step(const std::string path, std::vector<std::string> &files,bool getFolder = true); 
//只读列表下一层，true--带path
std::string makeDir(std::string dirPath);
std::string getSysTime(bool isNumStr = true);