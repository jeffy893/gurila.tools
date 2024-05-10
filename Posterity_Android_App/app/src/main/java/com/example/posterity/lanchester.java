package com.example.posterity;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import Jama.Matrix;

public class lanchester {

    double this_a;
    double this_b;
    double this_c;
    double this_d;
    double this_e;
    double this_f;
    double xprime;
    double yprime;
    int this_intervals;
    double num_people;
    int this_size;
    double[][] battle_graph;


    public lanchester(double size, int intervals, double a, double b, double c, double d, double e, double f) {

        this_a = a;
        this_b = b;
        this_c = c;
        this_d = d;
        this_e = e;
        this_f = f;
        this_intervals = intervals;
        num_people = size;



    }





    public void battle() {


        double[][] X = new double[101][2];

        X[0][0] = this_size;
        X[0][1] = this_size;

        double dt = 4.0 / 100.0;

        for (int i = 0; i < 100; ++i)
        {
            double t = i*dt;

            /* calculate derivatives */
            xprime = - this_a * X[i][0] * X[i][1] - this_b * X[i][1] + this_c*Math.cos(t) + this_c*t;
            yprime = - this_d * X[i][0]  - this_e  * X[i][0] * X[i][1] + this_f*Math.cos(t) + this_f*t;

            /* now integrate using Euler */
            X[i+1][0] = X[i][0] + xprime * dt;
            X[i+1][1] = X[i][1] + yprime * dt;

        }

        battle_graph = X;
    }

    public Set<double[][]> getGraphs(double cohc, int heatcount, double[] bdchain, int size, double flux_people, double cohdelta, double forcedelta){

        Set<double[][]> graphs = new HashSet<double[][]>();

        // Cattle Cohesion is fixed
        this_e = cohc;
        this_size = size;
        double max = bdchain[heatcount-1];

        for(int i = 0; i < heatcount; i++) {

            if(flux_people/num_people > (this_size/3)) {
                this_c = this_size/3;
            }else {
                this_c = flux_people/num_people;
            }

            this_a = (bdchain[i]/max)*(this_size/6);


            for(int j = 0; j < this_intervals; j++) {
                this_f = this_f + forcedelta;
                battle();
                graphs.add(battle_graph);
            }


        }

        return graphs;
    }

}
