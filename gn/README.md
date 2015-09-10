GN is a meta-build system that generates ninja files, which is part of the Chromium tree.
该工程用于熟悉gn的用法。

官方链接
======

Chromium 源码：
    https://chromium.googlesource.com/chromium/src/+/master/
Chromium 源码在线搜索：
    https://code.google.com/p/chromium/codesearch
文档：
    https://chromium.googlesource.com/chromium/src/+/master/tools/gn/
    https://code.google.com/p/chromium/wiki/gn
 
目录说明
=======

bin：预编译好的gn可执行文件
doc：收集的官方文档
note：自己实践中的笔记
src：工程示例


用法
======

下载安装
    1. 访问 Chromium 源码 https://chromium.googlesource.com/chromium/src/+/master/
    2. 在 DEPS 文件的 "name": "gn_mac" 部分得到 <bucket> 和 gn.sha1 的位置
        2.1. gn.sha1 位置，一般在 tools/gn/bin/mac/gn.sha1 或 buildtools/mac/gn.sha1 中，
        如果 gn.sha1 是位于 buildtools/mac/gn.sha1（buildtools.git）中，需要在文件中找到buildtools_revision，让后通过
            https://chromium.googlesource.com/chromium/buildtools.git/+/<buildtools_revision> 找到buildtools目录，例如
            https://chromium.googlesource.com/chromium/buildtools.git/+/565d04e8741429fb1b4f26d102f2c6c3b849edeb
    3. 根据gn.sha1文件内容的 得到<object>
    4. 通过 storage.googleapis.com/<bucket>/<object> 下载 gn binary
    5. 把 gn binary 添加到 PATH 中

构建配置
    1. copy本项目中的 //src/build 到工程中的 src root 下
    2. copy本项目中的 //src/.gn 到工程中的 src root 下
    3. 在 src root 下编辑 BUILD.gn

编译运行
    1. gn gen out/my_build
    2. gn args out/my_build // 可选
    3. ninja -C out/my_build
    4. cd out/my_build
       ./<executable bin>


