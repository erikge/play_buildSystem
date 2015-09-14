#include "jni_util.h"

#include <sys/types.h>
#include <assert.h>
#include <android/log.h>

#define LOG_TAG  "jni_util_cpp"




static JavaVM *s_jvm_ = NULL;

jint EXPORT_API JNI_OnLoad(JavaVM* vm, void* reserved)
{
    jint result = -1;

    JNIEnv* env = NULL;
    if (vm->GetEnv((void**) &env, JNI_VERSION_1_4) != JNI_OK) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] JNI_OnLoad failed!");
        goto bail;
    }
    assert(env != NULL);

    s_jvm_ = vm;
    jni_register_impl(env);

    __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, "[jni] JNI_OnLoad success");
    result = JNI_VERSION_1_4;
bail:
    return result;
}

static JNIEnv* jni_get_env() {
    if (s_jvm_ == NULL) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] *** jvm is NULL ***");
        return NULL;
    }
    JNIEnv *env = NULL;
    if (s_jvm_->GetEnv((void **)&env, JNI_VERSION_1_4) != JNI_OK) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] JNI_OnLoad failed!");
        return NULL;
    }
    return env;
}


int jni_register_method_table(const char *className, const JNINativeMethod *methodTable, int methodNum) {
    jint result = -1;
    JNIEnv* env = jni_get_env();
    if (env == NULL) {
        return result;
    }

    __android_log_print(ANDROID_LOG_INFO, LOG_TAG, "[jni] Registering native method table for %s\n", className);
    jclass clazz = env->FindClass(className);
    if (clazz == NULL) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] registerNative: unable to find class '%s'\n", className);
        return result;
    }
    if (env->RegisterNatives(clazz, methodTable, methodNum) < 0) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] registerNative: failed!\n");
        result = -1;
    } else {
        result = 0;
    }
    env->DeleteLocalRef(clazz);
    return result;
}


int jni_attach_java_thread(bool &fattach) {
    jint result = -1;
    JNIEnv* env = jni_get_env();
    if (env == NULL) {
        return result;
    }

    JavaVMAttachArgs args;
    args.version = JNI_VERSION_1_4;
    args.name = NULL;
    args.group = NULL;
    
    result = s_jvm_->AttachCurrentThread(&env, (void *)&args);
    if (result != JNI_OK) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] attach thread failed!");
    }
    fattach = (result == JNI_OK) ? true : false;
    return result;
}

int jni_detach_java_thread() {
    jint result = -1;
    if (s_jvm_ == NULL) {
        return result;
    }

    result = s_jvm_->DetachCurrentThread();
    if (result != JNI_OK) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] detach thread failed!");
    }
    return result;
}

int jni_throw_exception(const char *className, const char *msg) {
    jint result = -1;
    JNIEnv* env = jni_get_env();
    if (env == NULL) {
        return result;
    }

    jclass exceptionClass = env->FindClass(className);
    if (exceptionClass == NULL) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] Unable to find exception class %s", className);
        return result;
    }
    if (env->ThrowNew(exceptionClass, msg) != JNI_OK) {
        __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, "[jni] Failed throwing '%s' '%s'", className, msg);
    }
    env->DeleteLocalRef(exceptionClass);
    return 0;
}


jobject jni_create_java_object(const char *className, const char *initSig, ...) {
    JNIEnv* env = jni_get_env();
    if (env == NULL) {
        return NULL;
    }

    jclass clazz = env->FindClass(className);
    if (NULL == clazz) {
        return NULL;
    }
    jmethodID methodInit = env->GetMethodID(clazz, "<init>", initSig);
    if (NULL == methodInit) {
        return NULL;
    }

    va_list arList;
    va_start(arList, initSig);
    jobject objRet = env->NewObjectV(clazz, methodInit, arList);
    va_end(arList);

    env->DeleteLocalRef(clazz);
    return objRet; 
}

jint jni_get_int_field(const char *className, const char *fieldName, jobject instance) {
    jint result = -1;
    JNIEnv* env = jni_get_env();
    if (env == NULL) {
        return result;
    }

    jclass clazz = env->FindClass(className);
    if (NULL == clazz) {
        return result;
    }
    jfieldID fieldID = env->GetFieldID(clazz, fieldName, "I");
    if (NULL == fieldID) {
        return result;
    }

    jint ret = env->GetIntField(instance, fieldID);

    env->DeleteLocalRef(clazz);
    return ret;
}

jobject jni_get_object_field(const char *className, const char *fieldName, const char *fieldSig, jobject instance) {
    JNIEnv* env = jni_get_env();
    if (env == NULL) {
        return NULL;
    }

    jclass clazz = env->FindClass(className);
    if (NULL == clazz) {
        return NULL;
    }
    jfieldID fieldID = env->GetFieldID(clazz, fieldName, fieldSig);
    if (NULL == fieldID) {
        return NULL;
    }

    jobject ret = env->GetObjectField(instance, fieldID);

    env->DeleteLocalRef(clazz);
    return ret;
}

jint jni_get_static_int_field(const char *className, const char *fieldName) {
    jint result = -1;
    JNIEnv* env = jni_get_env();
    if (env == NULL) {
        return result;
    }

    jclass clazz = env->FindClass(className);
    if (NULL == clazz) {
        return result;
    }
    jfieldID fieldID = env->GetStaticFieldID(clazz, fieldName, "I");
    if (NULL == fieldID) {
        return result;
    }

    jint ret = env->GetStaticIntField(clazz, fieldID);

    env->DeleteLocalRef(clazz);
    return ret;
}




// TODO: 反射调用方法, 字符串/数组转换

