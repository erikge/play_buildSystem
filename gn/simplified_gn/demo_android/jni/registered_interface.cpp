#include "jni_util.h"

static const char* const s_class_path = "com/erikge/gnandroid/NativeInterface";

static jint minus_impl(JNIEnv *env, jclass clazz, jint x, jint y) {
    return x - y;
}


int jni_register_impl(JNIEnv *env) {
    JNINativeMethod methods_table[] = {
        {"minus", "(II)I",	(void *)minus_impl},
    };

    jni_register_method_table(s_class_path, methods_table, ARRAY_LEM(methods_table));
    return 0;
}

