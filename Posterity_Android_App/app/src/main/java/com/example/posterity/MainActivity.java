package com.example.posterity;

import android.graphics.Color;
import android.os.Bundle;


import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.android.material.snackbar.Snackbar;

import androidx.appcompat.app.AppCompatActivity;

import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.EditText;
import android.widget.SeekBar;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;

import lecho.lib.hellocharts.model.Axis;
import lecho.lib.hellocharts.model.AxisValue;
import lecho.lib.hellocharts.model.Line;
import lecho.lib.hellocharts.model.LineChartData;
import lecho.lib.hellocharts.view.LineChartView;


public class MainActivity extends AppCompatActivity {


    private EditText et2, et;
    private SeekBar sb2, sb;
    private TextView tv1, tv2, tv3, tv4, tv5, tv6;
    private double heat, pace, flux_people, num_people;
    LineChartView lineChartView;
    int[] axisData;
    List axisValues, lines;
    Line bLine, cLine;
    Axis axis, baxis;
    double[][] unexData, unexData7, unexData12;
    LineChartData data;
    boolean chart;
    int size;
    double wisdom;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);







        et2 = findViewById(R.id.editText2);
        et = findViewById(R.id.editText);
        sb2 = findViewById(R.id.seekBar2);
        sb = findViewById(R.id.seekBar);
        tv1 = findViewById(R.id.textView);
        tv2 = findViewById(R.id.textView2);
        tv3 = findViewById(R.id.textView3);
        tv4 = findViewById(R.id.textView4);
        tv5 = findViewById(R.id.textView5);
        tv6 = findViewById(R.id.textView6);
        lineChartView = findViewById(R.id.chart);
        heat = 0.5;
        pace = 0.5;
        flux_people = 1.0;
        num_people = 1.0;
        chart = false;


        FloatingActionButton fab = findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

            if(chart == true){

                lineChartView.setVisibility(View.INVISIBLE);
                et.setVisibility(View.VISIBLE);
                et2.setVisibility(View.VISIBLE);
                sb.setVisibility(View.VISIBLE);
                sb2.setVisibility(View.VISIBLE);
                tv1.setVisibility(View.VISIBLE);
                tv2.setVisibility(View.VISIBLE);
                tv3.setVisibility(View.VISIBLE);
                tv4.setVisibility(View.VISIBLE);
                tv5.setVisibility(View.VISIBLE);
                tv6.setVisibility(View.VISIBLE);

                chart = false;

            }else {

                flux_people = Double.parseDouble(et2.getText().toString());
                num_people = Double.parseDouble(et.getText().toString());

                sb.setMax(10000);
                sb2.setMax(10000);
                pace = (((double) sb2.getProgress() / 10000.0) * 0.125) + 0.02;
                heat = (((double) sb.getProgress() / 10000.0) * 0.8) + 0.1;

                //tv.setText("Num_People=" + num_people + ", Flux_People=" + flux_people + ", Heat=" + heat + ", Pace=" + pace);


                unexData = new double[100][2];
                unexData7 = new double[100][2];
                unexData12 = new double[100][2];

                for(int i=0; i < 100; i++) {

                    unexData[i][0] = 12.0;
                    unexData[i][1] = 12.0;
                    unexData7[i][0] = 12.0;
                    unexData7[i][1] = 12.0;
                    unexData12[i][0] = 12.0;
                    unexData12[i][1] = 12.0;
                }


                calculate compete = new calculate();

                size = 12;
                wisdom = 0.12;
                compete.battle(num_people, flux_people, pace, heat, size, wisdom);
                unexData = compete.getUnexData();
                compete.battle(num_people, flux_people, pace, heat, 7, 0.07);
                unexData7 = compete.getUnexData();
                compete.battle(num_people, flux_people, pace, heat, 3, 0.03);
                unexData12 = compete.getUnexData();

                if(unexData12[5][1] != 12.0){
                    unexData = unexData12;
                    size = 12;
                } else if(unexData7[5][1] != 12.0){
                    unexData = unexData7;
                    size = 7;
                } else {
                    size = 3;
                }





                axisValues = new ArrayList();

                axisData = new int[100];

                for (int i = 0; i < 100; i++) {
                    axisData[i] = i + 1;
                }

                for (int i = 0; i < i; i++) {
                    axisValues.add(i, new AxisValue(i).setLabel(String.valueOf(axisData[i]/4)));
                }



                lines lin = new lines(unexData);

                bLine = lin.this_bLine;
                cLine = lin.this_cLine;


                lines = new ArrayList();
                lines.add(bLine);
                lines.add(cLine);


                data = new LineChartData();
                data.setLines(lines);

                axis = new Axis();
                baxis = new Axis();
                axis.setValues(axisValues);
                baxis.setTextSize(16);
                axis.setTextSize(16);
                axis.setTextColor(Color.parseColor("#03A9F4"));
                baxis.setTextColor(Color.parseColor("#03A9F4"));



                data.setAxisXBottom(axis);
                data.setAxisYLeft(baxis);


                lineChartView.setLineChartData(data);


                et.setVisibility(View.INVISIBLE);
                et2.setVisibility(View.INVISIBLE);
                sb.setVisibility(View.INVISIBLE);
                sb2.setVisibility(View.INVISIBLE);
                tv1.setVisibility(View.INVISIBLE);
                tv2.setVisibility(View.INVISIBLE);
                tv3.setVisibility(View.INVISIBLE);
                tv4.setVisibility(View.INVISIBLE);
                tv5.setVisibility(View.INVISIBLE);
                tv6.setVisibility(View.INVISIBLE);
                lineChartView.setVisibility(View.VISIBLE);

                chart = true;

            }


            }
        });
    }



    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
}
