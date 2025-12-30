package com.example.posterity;


public class dance {


    double[] bdchain;
    int heatcount;

    public dance(double dance, double dancedelta, int size, double raw_dances_score) {


        // Come up with least count of state-steps to all bison or all cattle
        int dancecount = 0;
        double comeup = dance;
        double longevity = dance;
        while(comeup > 0 && longevity < 1) {
            comeup -= dancedelta;
            longevity += dancedelta;
            dancecount++;
            //System.out.println(dancecount);
        }


        double[] bdcomeup = new double[dancecount];
        comeup = dance - dancedelta;
        double comeupmax = 0.000001;
        double[] comeupdances = new double[size-2];
        Double comeupscore = 1.0;
        for(int i = 0; i < dancecount; i++) {
            comeupdances = ehrenfest.chain(size, comeup);
            for(int j = 0; j < size - 2; j++) {
                if(comeupmax > comeupdances[j]) {
                    comeupmax = comeupdances[j];
                }
            }
            if((int)(comeup*size)-3 >= comeupdances.length) {
                comeupscore = comeupdances[comeupdances.length-1]/comeupmax;
            }else if((int)(comeup*size)-3 < 0) {
                comeupscore = comeupdances[0]/comeupmax;
            }else {
                comeupscore = comeupdances[(int)(comeup*size)-3]/comeupmax;
            }
            bdcomeup[i] = comeupscore;
            comeup = comeup - dancedelta;
        }



        double[] bdlongevity = new double[dancecount];
        longevity = dance + dancedelta;
        double longevitymax = 1.0;
        double[] longevitydances = new double[size-2];
        double longevityscore = 1.0;
        for(int i = 0; i < dancecount; i++) {
            longevitydances = ehrenfest.chain(size, longevity);
            for(int j = 0; j < size - 2; j++) {
                if(longevitymax > longevitydances[j]) {
                    longevitymax = longevitydances[j];
                }
            }
            if((int)(longevity*size)-3 >= comeupdances.length) {
                longevityscore = longevitydances[longevitydances.length-1]/longevitymax;
            }else if((int)(longevity*size)-3 < 0) {
                longevityscore = longevitydances[0]/longevitymax;
            }else {
                longevityscore = longevitydances[(int)(longevity*size)-3]/longevitymax;
            }
            bdlongevity[i] = longevityscore;
            longevity = longevity + dancedelta;
        }



        double[] chain = new double[dancecount-2];
        chain = birthdeath.chain(bdcomeup, bdlongevity, raw_dances_score, dancecount);

        bdchain = chain;
        heatcount = dancecount-2;

    }


    public int getHeatcount() {
        return heatcount;
    }

    public double[] getBdchain() {
        return bdchain;
    }


}
