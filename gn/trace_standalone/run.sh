#! /bin/bash

start=$(date +%s)
# ======================

gn gen out/android --args='target_os = "android" target_cpu = "arm"'
#ninja -C out/android/ -t clean
ninja -C out/android/

# ======================
end=$(date +%s)
cost_time=$[$end - $start]
echo ""
echo "Total time: $cost_time seconds"
