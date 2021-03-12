cmake_minimum_required(VERSION 3.10.0)

project(l2dmgr)

add_executable(l2dmgr
    src/main
    src/compress
    src/snapshot
    src/listFiles
    src/kline
    )
target_include_directories(l2dmgr PUBLIC include)

project(klbf)

add_executable(klbf
    src/klineBFMain
    src/compress
    src/snapshot
    src/listFiles
    src/kline
    )
target_include_directories(klbf PUBLIC include)

project(klbfdb)

add_executable(klbfdb
    src/klineBFMain
    src/compress
    src/snapshot
    src/listFiles
    src/kline
    src/auction
    )
target_include_directories(klbfdb PUBLIC include)

find_package(qts-utils REQUIRED)
find_package(ZLIB REQUIRED)

target_link_libraries(l2dmgr PUBLIC qts-utils ${ZLIB_LIBRARY})
target_link_libraries(klbf PUBLIC qts-utils ${ZLIB_LIBRARY})
target_link_libraries(klbfdb PUBLIC qts-utils ${ZLIB_LIBRARY})

