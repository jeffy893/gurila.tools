package cortext;

public class prob_obj {
	
	Integer id;
	Float prob;
	Float time;
	
	public prob_obj(Integer i, Float p, Float t){
	
		id = i;
		prob = p;
		time = t;
		
	}
	
	
	public void updateProb(Float update){
		
		prob *= update;
		
	}

}
