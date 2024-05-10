package com.example.posterity;

import android.util.Log;

import org.apache.commons.math3.stat.regression.SimpleRegression;

import java.util.Set;

public class calculate {

    double[][] this_unexData;

    public calculate(){


        this_unexData = new double[100][2];

        for(int i=0; i < 100; i++) {
            this_unexData[i][0] = 12.0;
            this_unexData[i][1] = 12.0;
            //System.out.println(i + "," + bison[i][1] + "," + cattle[i][1]);
        }


    }


    public double[][] getUnexData(){
        return this_unexData;
    }


        public void battle(double num_people, double flux_people, double pace, double heat, int size, double wisdom){


            int intervals = (int) (4.0/pace); //Number of songs in 4 hours
            double heatdelta = 1.0/(4.0/pace); //For incrementing the heat variable at the end of each song
            // double wisdom = 0.12; This is gaussian for both sides but a necessary variable in the lanchester


            // This is the size of group that should be approached


            // increment force and cohesion for later battles
            double forcedelta = (size/3)/intervals;
            double cohdelta = (size/6)/intervals;
            double cohb = cohdelta; //cohesion at most one sixth of size
            double cohc = cohdelta;
            double forceb = forcedelta; // at most one third of size
            double forcec = forcedelta; //at most one third of size

            double[] raw_heats = new double[(int)num_people -2];
            // Raw heats at the beginning
            raw_heats = ehrenfest.chain(num_people, heat);
            double max_raw = 0.000001;
            for(int i = 0; i < (int)num_people - 2; i++) {
                if(max_raw > raw_heats[i]) {
                    max_raw = raw_heats[i];
                }
            }
            double raw_heats_score = raw_heats[(int)(heat*size)]/max_raw;
            lanchester raw_battle = new lanchester(num_people,intervals,cohb,wisdom,forceb,wisdom,cohc,forcec);


            dance equilibrium = new dance(0.5, heatdelta, size, raw_heats_score);
            Log.e("Animals",String.valueOf(num_people));
            Log.e("Flux",String.valueOf(flux_people));
            Log.e("Heat",String.valueOf(heat));
            Log.e("Pace", String.valueOf(pace));
            dance actual = new dance(heat, heatdelta, size, raw_heats_score);

            double[][] eqreg = new double[equilibrium.heatcount][2];
            for(int i = 0; i < equilibrium.heatcount; i++) {
                eqreg[i][0] = i;
                eqreg[i][1] = equilibrium.bdchain[i];
                //System.out.println(equilibrium.bdchain[i]);
            }

            double[][] actualreg = new double[actual.heatcount][2];
            for(int i = 0; i < actual.heatcount; i++) {
                actualreg[i][0] = i;
                actualreg[i][1] = actual.bdchain[i];
                //System.out.println(actual.bdchain[i]);
            }


            SimpleRegression eqobj = new SimpleRegression();
            SimpleRegression actualobj = new SimpleRegression();
            eqobj.addData(eqreg);
            actualobj.addData(actualreg);
            double eqslope = eqobj.getSlope();
            double actualslope = actualobj.getSlope();


            cohc = (actualslope/eqslope)*(size/6);
            //System.out.println(cohc);
            Set<double[][]> graphs = raw_battle.getGraphs(cohc, actual.heatcount, actual.bdchain, size, flux_people, cohdelta, forcedelta);


            boolean oneneutral = false;
            boolean oneepic = false;
            boolean oneunexpected = false;


            double[][] unexData = new double[100][100];
            double[][] epicData = new double[100][100];
            double[][] neutralData = new double[100][100];

            for(double[][] graph : graphs) {

                double[][] bison = new double[100][2];
                double[][] cattle = new double[100][2];




                boolean neutral1 = false;
                boolean neutral2 = false;
                boolean unexpected = false;
                boolean bisonmax1 = false;
                boolean bisonmax2 = false;
                boolean epic = false;
                if(graph[1][0] > graph[1][1]) {
                    bisonmax1 = true;
                }else {
                    bisonmax1 = false;
                }

                bison[0][1] = size;
                cattle[0][1] = size;

                for(int i=1; i < 100; i++) {
                    bison[i][0] = i;
                    cattle[i][0] = i;
                    bison[i][1] = graph[i][0];
                    cattle[i][1] = graph[i][1];


                    if(unexpected == true && epic == false) {
                        if(bisonmax2 == true && graph[i][1] > graph[i][0]) {
                            epic = true;
                        }
                        if(bisonmax2 == false && graph[i][1] < graph[i][0]) {
                            epic = true;
                        }
                    }

                    if(unexpected == false) {
                        if(bisonmax1 == true && graph[i][1] > graph[i][0]) {
                            unexpected = true;
                            bisonmax2 = false;
                        }
                        if(bisonmax1 == false && graph[i][1] < graph[i][0]) {
                            unexpected = true;
                            bisonmax2 = true;
                        }
                    }



                    if(graph[i][0] < 0 || graph[i][1] < 0) {
                        neutral1 = true;
                    }
                    if(graph[i][0] < 0 && graph[i][1] < 0) {
                        neutral2 = true;
                    }
                    if(graph[i][0] > size || graph[i][1] > size) {
                        neutral1 = true;
                    }
                    Double nanb = graph[i][0];
                    Double nanc = graph[i][1];
                    if(nanb.isNaN() || nanc.isNaN()) {
                        neutral2 = true;
                    }


                }


                if(neutral2 == false) {
                    if(neutral1 == false && oneneutral == false){
                        //System.out.println("Neutral");
                        for(int i=0; i < 100; i++) {

                            neutralData[i][0] = bison[i][1];
                            neutralData[i][1] = cattle[i][1];
                            //System.out.println(i + "," + bison[i][1] + "," + cattle[i][1]);
                        }
                        oneneutral = true;
                    }
                    if(epic == true && oneepic == false) {
                        //System.out.println("Epic");
                        for(int i=0; i < 100; i++) {

                            epicData[i][0] = bison[i][1];
                            epicData[i][1] = cattle[i][1];
                            //System.out.println(i + "," + bison[i][1] + "," + cattle[i][1]);
                        }
                        oneepic = true;
                    }
                    if(unexpected == true && oneunexpected == false) {
                        //System.out.println("Unexpected");
                        for(int i=0; i < 100; i++) {
                            unexData[i][0] = bison[i][1];
                            unexData[i][1] = cattle[i][1];
                            //System.out.println(i + "," + bison[i][1] + "," + cattle[i][1]);
                        }
                        oneunexpected = true;
                    }
                }

            } //For Graphs

            if (oneunexpected == false){
                //System.out.println("Unexpected");
                for(int i=0; i < 100; i++) {
                    unexData[i][0] = 12.0;
                    unexData[i][1] = 12.0;
                    //System.out.println(i + "," + bison[i][1] + "," + cattle[i][1]);
                }
                oneunexpected = true;
            }

            if(oneepic == false) {
                //System.out.println("Epic");
                for(int i=0; i < 100; i++) {

                    epicData[i][0] = 12.0;
                    epicData[i][1] = 12.0;
                    //System.out.println(i + "," + bison[i][1] + "," + cattle[i][1]);
                }
                oneepic = true;
            }

            if(oneneutral == false){
                //System.out.println("Neutral");
                for(int i=0; i < 100; i++) {

                    neutralData[i][0] = 12.0;
                    neutralData[i][1] = 12.0;
                    //System.out.println(i + "," + bison[i][1] + "," + cattle[i][1]);
                }
                oneneutral = true;
            }

            if(epicData[5][0] != 12.0){
                this_unexData = epicData;
            }else if(unexData[5][0] != 12.0){
                this_unexData = unexData;
            } else{
                this_unexData = neutralData;
            }


        }// Method


}
