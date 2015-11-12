#! /bin/bash

start=$(date +%s)
# ======================

gn/bin/gn gen out/java --args='target_os = "android" is_java=true'
gn/bin/ninja -C out/java/

# ======================
end=$(date +%s)
cost_time=$[$end - $start]
echo ""
echo "Total time: $cost_time seconds"
