play_gn
=======

GN is a meta-build system that generates ninja files. It's meant to be faster and simpler than GYP. It outputs Ninja build files.

GN is part of the Chromium tree.

I want to figure out how to use it in this repo.


1. Set up the environment

* "depot_tools" in PATH
* ".gclient" file and "buildtools" path to locate gn binary
or
* put self-build gn binary in PATH

2. 

* put a ".gn" file in a directory as "source root"


3. gn usage

gn gen out/mybuild
ninja -C out/mybuild

Summary
=======

gn is in very earily-stage, and not work well in stand along project. I decided to try it later in the future.


