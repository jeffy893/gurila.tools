package com.example.posterity;

import Jama.Matrix;


public class birthdeath {


    static double[] chain(double[] comeup, double[] longevity, double raw_dances_score, int intervals) {

        double total = 1.0;

        double[][] bdchain = new double[intervals][intervals];
        double[][] identity = new double[intervals][intervals];

        for(int i = 0; i < intervals; i++) {
            for(int j = 0; j < intervals; j++) {

                total = comeup[i] + longevity[i] + raw_dances_score;

                if(j == i - 1) {
                    bdchain[i][j] = comeup[i]/total;
                }else if(j == i + 1) {
                    bdchain[i][j] = longevity[i]/total;
                }else if(i == j){
                    bdchain[i][j] = raw_dances_score/total;
                }
            }
        }

        for(int i = 0; i < intervals; i++) {
            for(int j = 0; j < intervals; j++) {
                if(j == i) {
                    identity[i][j] = 1;
                }else {identity[i][j] = 0;}
            }
        }

        Matrix ehr = new Matrix(bdchain);
        Matrix id = new Matrix(identity);

        double[][] one = new double[intervals][1];

        for(int i = 0; i < intervals; i++) {
            one[i][0] = 1;
        }

        Matrix ones = new Matrix(one);

        Matrix inverse = id.minus(ehr).getMatrix(1,intervals-2,1,intervals-2).inverse();

        Matrix solution = inverse.times(ones.getMatrix(1,intervals-2,0,0));



        double[] final_sol = new double[intervals-2];

        for(int i = 0; i < intervals-2; i++){
            final_sol[i] = solution.get(i,0);
        }



        return final_sol;

    }


}
