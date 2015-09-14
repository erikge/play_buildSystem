LOCAL_PATH:= $(call my-dir)

include $(CLEAR_VARS)

LOCAL_SRC_FILES := \
	com_erikge_gnandroid_NativeInterface.cpp \

LOCAL_LDLIBS := -llog

LOCAL_CFLAGS += -Wno-multichar
LOCAL_MODULE_TAGS := optional



LOCAL_MODULE:= ttest

include $(BUILD_SHARED_LIBRARY)
