package cortext;

import Jama.Matrix;

public class CurveFit {
  public static String fit(int points, String data, double yIntercept) {
    double[] exes = new double[points];
    double[][] whys = new double[points][1];
    double[][] matrix = new double[points][points];
    String[] point = data.split("\n");
    for (int a = 0; a < point.length; a++) {
      String[] xy = point[a].split(",");
      exes[a] = Double.parseDouble(xy[0]);
      whys[a][0] = Double.parseDouble(xy[1]) - yIntercept;
    } 
    for (int b = 0; b < points; b++) {
      double order = points;
      for (int c = 0; c < points; c++) {
        matrix[b][c] = Math.pow(exes[b], order);
        order--;
      } 
    } 
    Matrix A = new Matrix(matrix);
    Matrix matrix1 = new Matrix(whys);
    Matrix x = A.solve(matrix1);
    String equation = "";
    double[][] xprint = x.getArray();
    int variable = points;
    for (int d = 0; d < xprint.length; d++) {
      equation = equation + xprint[d][0] + "* x^" + variable + " + ";
      variable--;
    } 
    return equation + yIntercept;
  }
}
