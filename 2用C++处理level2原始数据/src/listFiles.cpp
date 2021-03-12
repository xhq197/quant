#include "listFiles.h"
#include <filesystem>
#include <time.h>

using namespace std;
namespace fs = std::filesystem;


void getFiles(const std::string path, std::vector<std::string> &files,bool getFolder)
{
  DIR *dir;
  struct dirent *ptr;

  if ((dir = opendir(path.c_str())) == NULL)
  {
    perror("Open dir error...");
    exit(1);
  }

  while ((ptr = readdir(dir)) != NULL)
  {
    if (strcmp(ptr->d_name, ".") == 0 || strcmp(ptr->d_name, "..") == 0)
      continue;
    else if (ptr->d_type == 8)
    {
      if(!getFolder){
        ///string str1 = "/mnt/data_backup/L2SH/2014/20140715/"
        ///get file path, ex: /mnt/data_backup/L2SH/2014/20140715/Snapshot.7z.001
        files.push_back(path + ptr->d_name);
        // cout<<path + ptr->d_name<<endl;
      }
      else{
        continue;
      }
        
    }
      
    else if (ptr->d_type == 10)
    {
      continue;
    }
      
      
    else if (ptr->d_type == 4)
    {
      if(getFolder){
        //get folder path, ex: /mnt/data_backup/L2SH/2014/20140714
        files.push_back(path + ptr->d_name);
        // cout<<path + ptr->d_name<<endl;
      }
        
      getFiles(path + ptr->d_name + "/", files);
    }
  }
  closedir(dir);
}

string makeDir(std::string dirPath)
{
	if(!fs::exists(dirPath)) fs::create_directories(dirPath);
  return dirPath;
}
		
void getFiles1Step(const std::string path, std::vector<std::string> &files,bool getFolder)
{
  DIR *dir;
  struct dirent *ptr;

  if ((dir = opendir(path.c_str())) == NULL)
  {
    perror("Open dir error...");
    exit(1);
  }

  while ((ptr = readdir(dir)) != NULL)
  {
    if (strcmp(ptr->d_name, ".") == 0 || strcmp(ptr->d_name, "..") == 0)
      continue;
    else if (ptr->d_type == 8)
    {
      continue;        
    }
      
    else if (ptr->d_type == 10)
    {
      continue;
    }
      
      
    else if (ptr->d_type == 4)
    {
      if(!getFolder){
        //get folder path, ex: /mnt/data_backup/L2SH/2014/20140714
        files.push_back(ptr->d_name);
        // cout<<ptr->d_name<<endl;
      }
      else
      {
        files.push_back(path+ptr->d_name);
        // cout<<path+ptr->d_name<<endl;
        
      }
      
    }
  }
  closedir(dir);
}


std::string getSysTime(bool isNumStr)
{
  char sysTime[100];
  time_t tt;
  time( &tt );
  tt = tt + 8*3600;  // transform the time zone
  tm* t= gmtime( &tt );
  cout << tt << endl;
  if(!isNumStr)
  sprintf(sysTime,"%d-%02d-%02d %02d:%02d:%02d\n",
          t->tm_year + 1900,
          t->tm_mon + 1,
          t->tm_mday,
          t->tm_hour,
          t->tm_min,
          t->tm_sec);
  else
  sprintf(sysTime,"%d%02d%02d%02d%02d%02d",
          t->tm_year + 1900,
          t->tm_mon + 1,
          t->tm_mday,
          t->tm_hour,
          t->tm_min,
          t->tm_sec);
  
  string sysT(sysTime);
  return sysT; 
}