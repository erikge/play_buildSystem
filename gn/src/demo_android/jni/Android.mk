LOCAL_PATH:= $(call my-dir)

include $(CLEAR_VARS)

LOCAL_SRC_FILES := \
	3rd_so.cpp \
	jni_util.cpp \

LOCAL_LDLIBS := -llog

LOCAL_CFLAGS += -Wno-multichar
LOCAL_MODULE_TAGS := optional



LOCAL_MODULE:= style_3rd

include $(BUILD_SHARED_LIBRARY)
