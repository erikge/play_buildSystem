package com.erikge.gnandroid;

import java.lang.System;

/**
 * Created by erikge on 15/9/13.
 */
public class NativeInterface {

    static {
        System.out.println("[jni] load lib");
        System.loadLibrary("native_math");
//        System.loadLibrary("ttest");
    }

    public static native int add(int x, int y);
}
