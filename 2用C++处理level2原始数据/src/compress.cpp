#include "compress.h"

using namespace qts;

using namespace std;
namespace fs = std::filesystem;

std::string qts::utils::uncompressread(FILE *source, const size_t CHUNKIN){
  const size_t CHUNKOUT = 50 * CHUNKIN > 10000000 ? 10000000 : 50 * CHUNKIN;

  string outstring;

  unsigned char* in = new unsigned char[CHUNKIN];
  unsigned char* out = new unsigned char[CHUNKOUT];

  z_stream strm;

  /* allocate inflate state */
  strm.zalloc = Z_NULL;
  strm.zfree = Z_NULL;
  strm.opaque = Z_NULL;
  strm.avail_in = 0;
  strm.next_in = Z_NULL;
  int ret = inflateInit(&strm);
  if (ret != Z_OK)
    throw(runtime_error("uncompress error"));

  /* decompress until deflate stream ends or end of file */
  do {
    strm.avail_in = static_cast<uInt>(fread(in, static_cast<uInt>(1),
                                            static_cast<uInt>(CHUNKIN), source));
    if (ferror(source)) {
      (void)inflateEnd(&strm);
      delete[] in; delete[] out;
      throw(runtime_error("uncompress error"));
    }
    if (strm.avail_in == 0)
      break;
    strm.next_in = in;

    /* run inflate() on input until output buffer not full */
    do {

      strm.avail_out = static_cast<uInt>(CHUNKOUT);
      strm.next_out = out;

      ret = inflate(&strm, Z_NO_FLUSH);
      assert(ret != Z_STREAM_ERROR);  /* state not clobbered */
      switch (ret) {
        case Z_NEED_DICT:
          ret = Z_DATA_ERROR;     /* and fall through */
        case Z_DATA_ERROR:
        case Z_MEM_ERROR:
          (void)inflateEnd(&strm);
          delete[] in; delete[] out;
          throw(runtime_error("uncompress error"));
      }

      size_t have = CHUNKOUT - strm.avail_out;

      outstring.append(reinterpret_cast<char*>(out), have);

    } while (strm.avail_out == 0);

    /* done when inflate() says it's done */
  } while (ret != Z_STREAM_END);

  /* clean up and return */
  (void)inflateEnd(&strm);
  delete[] out;
  delete[] in;

  return outstring;
}

bool qts::utils::compresswrite(const std::string & fileName, const char* str, size_t N)
{
  unsigned long inLen = static_cast<unsigned long>(N);
  unsigned long outLen = 2 * inLen;
  unsigned char* outArray = new unsigned char[outLen];

  if (compress(outArray, &outLen,
               reinterpret_cast<const unsigned char*>(str), inLen) != 0) {
    delete[] outArray;
    return false;
  }

  FILE* f = fopen(fileName.c_str(), "wb");
  if (f == nullptr) {
    delete[] outArray;
    return false;
  }

  if (outLen != fwrite(outArray, sizeof(unsigned char), outLen, f)) {
    fclose(f);
    fs::remove(fileName);

    delete[] outArray;
    return false;
  }

  fclose(f);

  delete[] outArray;

  return true;
}
