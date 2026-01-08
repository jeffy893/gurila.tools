package cortext;

import java.util.ArrayList;

public class event_obj {
	
	int id;
	Float time;
	ArrayList<String> subject;
	ArrayList<String> concept;
	ArrayList<String> relation;
	Float prob;
	ArrayList<Integer> dep;
	
	
	public event_obj(int i, Float t, ArrayList<String> s, ArrayList<String> c,
			ArrayList<String> r, Float p, ArrayList<Integer> d){
		
		id = i;
		time = t;
		subject = s;
		concept = c;
		relation = r;
		prob = p;
		dep = d;
		
	}
	
	public void updateProb(Float update){
		
		prob *= update;
		
	}
	
	public void setProb(Float update){
		
		prob = update;
		
	}

}