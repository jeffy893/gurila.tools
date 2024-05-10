package com.example.posterity;

import android.graphics.Color;

import java.util.ArrayList;
import java.util.List;

import lecho.lib.hellocharts.model.AxisValue;
import lecho.lib.hellocharts.model.Line;
import lecho.lib.hellocharts.model.PointValue;

public class lines {

    Line this_cLine, this_bLine;


    public lines(double[][] data){

        List<PointValue> bAxisValues = new ArrayList();
        List<PointValue> cAxisValues = new ArrayList();


        Line bLine = new Line(bAxisValues).setColor(Color.parseColor("#008080"));
        Line cLine = new Line(cAxisValues).setColor(Color.parseColor("#800000"));


        for (int i = 0; i < 100; i++){
            bAxisValues.add(new PointValue(i, (float)data[i][0]));
        }
        for (int i = 0; i < 100; i++){
            cAxisValues.add(new PointValue(i, (float)data[i][1]));
        }





        this_bLine = bLine;
        this_cLine = cLine;
    }


}
