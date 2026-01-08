package cortext;

import java.util.ArrayList;
import java.util.Scanner;
import java.lang.Math;

public class Main {

	/**
	 * RK4 is an algorithm used to predict the solution of a differential equation.
	 * The reason why a differential equation is so difficult to solve is that most change does not happen
	 * 		in perfect oscillation.
	 * 
	 * 
	 * This application is the beta, of an android app, so as to test out the bugs.
	 * 
	 * One dependent variable
	 * 
	 * @param difeq
	 * I will need to have a string input for the differential equation
	 * @param domain
	 * I will need to have a string input for the domain (independent variable)
	 * 
	 * 
	 * Next I will need to calculate L1, L2, L3, L4
	 * 
	 * @param args
	 */
	
	
	public static void main(String[] args) {
		
		
		org.nfunk.jep.JEP myParser = new org.nfunk.jep.JEP();
		myParser.addStandardFunctions();
		myParser.addStandardConstants();
		myParser.addVariable("x", 8);
		myParser.addVariable("t", 8);
		
		/*
		
		myParser.parseExpression("x+t");
		
		double result = myParser.getValue();
		
		System.out.println(result);
		
		*/
		
		Scanner sc = new Scanner(System.in);
		boolean eqTrig = false;
		String difeq = "";
		
		System.out.println("RK4 Algorithm\n");
		System.out.println("Enter Differential Equation: ");
		while(eqTrig == false){
			try{
				difeq = sc.nextLine();
				myParser.parseExpression(difeq);
				eqTrig = true;
			} catch(Exception e){
				eqTrig = false;
				System.out.println("Bad Notation. Re-enter Differential Equation: ");
			}
			
		}
		
		System.out.println("Initial Value: ");
		double iv = sc.nextDouble();
		System.out.println("Enter Lower Bound: ");
		double lb = sc.nextDouble();
		System.out.println("Enter Upper Bound: ");
		double ub = sc.nextDouble();
		System.out.println("Enter # of Steps: ");
		int steps = sc.nextInt();
		
		int index = 0;
		
		ArrayList<function> total = new ArrayList<function>();
		
		total.add(new function(index, lb, iv));
		
		index++;
		
		double step = (ub-lb)/steps;
		
		
		for(int i = 0; i < steps; i++){
			myParser.addVariable("t", lb);
			myParser.addVariable("x", iv);
			double l1 = myParser.getValue();
			myParser.addVariable("t", lb + (step/2));
			myParser.addVariable("x", iv + ((step/2)*l1));
			double l2 = myParser.getValue();
			myParser.addVariable("t", lb + (step/2));
			myParser.addVariable("x", iv + ((step/2)*l2));
			double l3 = myParser.getValue();
			myParser.addVariable("t", lb + step);
			myParser.addVariable("x", iv + (step*l3));
			double l4 = myParser.getValue();
			
			double thisValue = iv + (step/6)*(l1+(2*l2)+(2*l3)+l4);
			
			
			total.add(new function(index, lb + step, thisValue));
			
			
			index++;
			lb += step;
			iv = thisValue;
			
			
			
		}
		
		
		System.out.println("-------------------------------------------------------");
		System.out.println("|\tt\t|\tx\t|");
		System.out.println("-------------------------------------------------------");
		
		
		
		for(int i = 0; i < total.size(); i++){
			
			
			for(function f: total){
				
				if(f.index == i){
					
					System.out.println("|\t" + String.format("%.5f", f.time) + "\t|\t" + String.format("%.5f", f.dep) + "\t|");
					
					
				}
				
				
			}
			
			
			
			
		}
		
		
		System.out.println("-------------------------------------------------------");
		
		
		
		
	}

	
	
	
}
