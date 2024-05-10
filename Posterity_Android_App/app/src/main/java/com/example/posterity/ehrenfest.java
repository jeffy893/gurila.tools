package com.example.posterity;

import java.util.HashSet;
import java.util.Set;

import Jama.Matrix;

public class ehrenfest {


    // 0 state ends up all cattle

    static double[] chain(double people, double dance) {

        int num_people = (int) people;

        int bison = (int) Math.round(dance*people);


        double[][] ehrenfest = new double[num_people][num_people];
        double[][] identity = new double[num_people][num_people];

        for(int i = 0; i < num_people; i++) {
            for(int j = 0; j < num_people; j++) {
                if(j == i - 1) {
                    ehrenfest[i][j] = bison/people;
                }else if(j == i + 1) {
                    ehrenfest[i][j] = 1 - (bison/people);
                }else {
                    ehrenfest[i][j] = 0;
                }
            }
        }

        for(int i = 0; i < num_people; i++) {
            for(int j = 0; j < num_people; j++) {
                if(j == i) {
                    identity[i][j] = 1;
                }else {identity[i][j] = 0;}
            }
        }

        Matrix ehr = new Matrix(ehrenfest);
        Matrix id = new Matrix(identity);


        double[][] one = new double[num_people][1];

        for(int i = 0; i < num_people; i++) {
            one[i][0] = 1;
        }

        Matrix ones = new Matrix(one);

        Matrix inverse = id.minus(ehr).getMatrix(1,num_people-2,1,num_people-2).inverse();

        Matrix solution = inverse.times(ones.getMatrix(1,num_people-2,0,0));

        double[] final_sol = new double[num_people-2];

        for(int i = 0; i < num_people-2; i++){
            final_sol[i] = solution.get(i,0);
        }

        return final_sol;

    }

}
