#ifndef __JNI_UTIL_H__
#define __JNI_UTIL_H__

#include "jni.h"

#ifndef ARRAY_LEM
#define ARRAY_LEM(x) ((int) (sizeof(x) / sizeof((x)[0])))
#endif // ARRAY_LEM

#ifndef EXPORT_API
#define EXPORT_API  __attribute__ ((visibility ("default")))
#endif

/**
 * Demo: 
 * static JNINativeMethod nativeMethodTable[] = {
		{"putByteArray2ByteBuffer","(Ljava/nio/ByteBuffer;I[BIIII)Z",	(void *)putByteArray2ByteBuffer},
		{"writeInputData","(Ljava/nio/ByteBuffer;)I",	(void *)writeInputData},
		{"writeInputData2","(Ljava/nio/ByteBuffer;I)I",	(void *)writeInputData2},
		{"readOutputData","(Ljava/nio/ByteBuffer;IIIIIIIIII)I",	(void *)readOutputData},
		{"readOutputDataEx","(Ljava/nio/ByteBuffer;IIIIIIII)I",	(void *)readOutputDataEx},
		{"readOutputStream","(Ljava/nio/ByteBuffer;JIII)I",	(void *)readOutputStream},
		{"setAVCParams","(Ljava/nio/ByteBuffer;Ljava/nio/ByteBuffer;)I", (void *)setAVCParams},
		{"attachCodec","(Ljava/lang/Object;)Z",	(void *)attachCodec},
		{"detachCodec","()V",	(void *)detachCodec},
		{"set_device_infos","(Ljava/lang/String;)V",	(void *)set_device_infos},
}; 
 * jni_register_method_table(className, nativeMethodTable, ARRAY_LEM(nativeMethodTable));
 * 
 * @param className 
 * @param methodTable 
 * 
 * @return int 
 */
int jni_register_method_table(const char *className, const JNINativeMethod *methodTable, int methodNum);

/**
 * A JNI interface pointer (JNIEnv*) is passed as an argument 
 * for each native function mapped to a Java method, allowing 
 * for interaction with the JNI environment within the native 
 * method.This JNI interface pointer can be stored, but remains 
 * valid only in the current thread. Other threads must first 
 * call AttachCurrentThread()to attach themselves to the VM and 
 * obtain a JNI interface pointer. Once attached, a native 
 * thread works like a regular Java thread running within a 
 * native method. The native thread remains attached to the VM 
 * until it callsDetachCurrentThread() to detach itself. 
 * 
 * @param fattach 
 * 
 * @return int 
 */
int jni_attach_java_thread(bool &fattach);

/**
JNIEnv和jobject对象都不能跨线程使用
 
    对于jobject，解决办法是
    a、g_obj = env->NewGlobalRef(obj);//创建一个全局变量  
    b、jobject obj = env->AllocObject(clazz);//在每个线程中都生成一个对象
 
    对于JNIEnv，解决办法是在每个线程中都重新生成一个env
    JNIEnv *env;  
    jvm->AttachCurrentThread((void **)&env, NULL);
 * 
 * @return int 
 */
int jni_detach_java_thread();

/**
 * Demo: 
 * jni_throw_exception("java/lang/RuntimeException", "something 
 * is wrong"); 
 * 
 * @param className 
 * @param msg 
 * 
 * @return int 
 */
int jni_throw_exception(const char *className, const char *msg);


/**
 * Demo: 
 * jni_create_java_object("java/lang/Integer", "(I)V", 32);
 * 
 * 
 * @param env 
 * @param className 
 * @param initSig 
 * 
 * @return jobject 
 */
jobject jni_create_java_object(const char *className, const char *initSig, ...);

/**
 * Demo: 
 * jni_get_int_field("android/view/Surface", 
 *  "mNativeObject", surface_instance);
 * 
 * @param className 
 * @param fieldSig 
 * @param instance 
 * 
 * @return jint 
 */
jint jni_get_int_field(const char *className, const char *fieldName, jobject instance);

/**
 * Demo: 
 * jni_get_int_field("android/view/Surface", 
 *  "mName", "Ljava/lang/String;", surface_instance);
 * 
 * @param className 
 * @param fieldName 
 * @param fieldSig 
 * @param instance 
 * 
 * @return jobject 
 */
jobject jni_get_object_field(const char *className, const char *fieldName, const char *fieldSig, jobject instance);


extern int jni_register_impl(JNIEnv *env);

#endif /* __JNI_UTIL_H__ */



