#include "com_erikge_gnandroid_NativeInterface.h"

JNIEXPORT jint JNICALL Java_com_erikge_gnandroid_NativeInterface_add
  (JNIEnv *env, jclass clazz, jint x, jint y) {
    return x + y;
}
