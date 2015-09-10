package com.erik.gn;

import com.erik.library.DemoMath;
import com.erik.library.DemoPrint;

public class Demo {

    public static void main(String[] args) {
        DemoPrint.hello();

        System.out.println("Test Add: " + DemoMath.add(1, 1));
    }
}