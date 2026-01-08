package cortext;

import java.util.ArrayList;
import java.util.Scanner;

public class Main {

	/**
	 * 
	 * Minute Phen
	 * 
	 * Application meant to help with the modeling of nature (natural philosophy)
	 * using an interventionist approach. The approach is considered interventionist
	 * because the end goal of each calculation is to determine a premium so as to either
	 * mitigate bad or
	 * promote good or
	 * ensure fairness
	 * 
	 * This Java Project will use a basic command line input and output.
	 * The code will then be transformed to layout into a phone (or wearable device) app
	 * 
	 * 
	 * The probability parameter is the most difficult to submit. The entries are parsed by comma,
	 * like all of the other parameters, but the first entry is the current prob. and the
	 * following prob. are integers of the id of dependent events. All events, already submitted,
	 * will be printed out at the beginning of each new event submission.
	 * 
	 * @param args
	 */
	
	
	public static void main(String[] args) {
		
		// Event Thread
		ArrayList<event_obj> thread = new ArrayList<event_obj>();
		ArrayList<prob_obj> arrayProb = new ArrayList<prob_obj>();
		
		
		Scanner sc = new Scanner(System.in);
		int home_trig = 0;
		int id = 0;
		while(home_trig != 4){
		
		switch(home_trig){
			case 0:
				System.out.println("\nMinute Phen - Minute Men Who Model Phen\n");
				System.out.println("Enter 1 - To Submit New Event\n");
				System.out.println("Enter 2 - To Calculate Probable Event Thread\n");
				System.out.println("Enter 3 - To Clear Event Thread\n");
				System.out.println("Enter 4 - To Exit\n");
				home_trig = sc.nextInt();
				break;
			case 1:
				
				// Print all previous events
				
				if(!thread.isEmpty()){
					

					System.out.println("\nPrevious Events\n");
					
					for(event_obj event: thread){
						
						System.out.println("id: " + event.id);
							System.out.print("time: " + event.time);
						System.out.print("\nSubjects: ");
						for(String s: event.subject){
							System.out.print(s + ",");
						}
						System.out.print("\nRelations: ");
						for(String r: event.relation){
							System.out.print(r + ",");
						}
						System.out.print("\nConcepts: ");
						for(String c: event.concept){
							System.out.print(c + ",");
						}
						System.out.print("\nDependecies: ");
						for(Integer d: event.dep){
							System.out.print(d + ",");
						}
						System.out.print("\n");
							System.out.print("Prob: " + event.prob);
						System.out.print("\n");
						System.out.println("\n");
						
						
					}
					
					
				}
				
				String times = "";
				String probs = "";
				
				
				System.out.println("\nSubmit Your Event\n");
				sc.nextLine();
				boolean timeBool = false;
				while(timeBool == false){
				System.out.println("\nTime: ");
				times = sc.nextLine();
				
					try{
						Float.parseFloat(times);
						// System.out.println("Test: " + times);
						timeBool = true;
					}catch(NumberFormatException e){
						System.out.println("Please enter a float");
						timeBool = false;
					}
				
				
				}
				System.out.println("\nSubjects: ");
				String subjects = sc.nextLine();
				System.out.println("\nRelations: ");
				String relations = sc.nextLine();
				System.out.println("\nConcepts: ");
				String concepts = sc.nextLine();
				boolean probBool = false;
				while(probBool == false){
					System.out.println("\nProbability (From 0 to 1): ");
					probs = sc.nextLine();
					
						try{
							Float.parseFloat(probs);
							// System.out.println("Test: " + times);
							probBool = true;
						}catch(NumberFormatException e){
							System.out.println("Please enter a float");
							probBool = false;
						}
					
					
					}
				System.out.println("\nDependencies (Enter " + id + " if none): ");
				String deps = sc.nextLine();
				
				
				
				Float time = Float.parseFloat(times);					// This time - for use in the prob_obj
				
				
				String[] subject = subjects.split(",");
					ArrayList<String> arraySubject = new ArrayList<String>();
					for(int i = 0; i < subject.length; i++){
						arraySubject.add(subject[i]);
					}
				String[] relation = relations.split(",");
					ArrayList<String> arrayRelation = new ArrayList<String>();
					for(int i = 0; i < relation.length; i++){
						arrayRelation.add(relation[i]);
					}
				String[] concept = concepts.split(",");
					ArrayList<String> arrayConcept = new ArrayList<String>();
					for(int i = 0; i < concept.length; i++){
						arrayConcept.add(concept[i]);
					}
				
				Float thisProb = Float.parseFloat(probs);						// This probability
				
				String[] dep = deps.split(",");
				
						ArrayList<Integer> arrayDep = new ArrayList<Integer>();
						for(int i = 0; i < dep.length; i++){
							arrayDep.add(Integer.parseInt(dep[i]));
						}
				
						
						arrayProb.add(new prob_obj(id,thisProb,time)); 			// Independent Probability record - Use to go back through dependencies
				
				
					
					
				thread.add(new event_obj(id, time, arraySubject, arrayRelation, arrayConcept, thisProb, arrayDep));
					
					
					
					
					
				
				
				home_trig = 0;
				id++;
				break;
			
				
				
				
				
			case 2:
				
				System.out.println("Most likely sequence of events (timeline)\n");
				
				
				// Prob. Based calculation. Then refer back to metadata of events using id. Assuming event entry in 
				
				for(prob_obj p: arrayProb){ // Iterate through independent array of prob.
					
					// Float rawProb = p.prob;
					
					for(event_obj e: thread){ // Iterate through events
						
						// Naive approach
						
						for(Integer d_id: e.dep){ // Iterate through dependencies
							
							if(p.id == d_id){     // If the id of the dependency equals the id of the current probability
								
								// System.out.println("Test Dependency is: " + d_id);
								/*for(prob_obj p2: arrayProb){ // Iterate through the independent prob. again
								
									
									if(p2.id == d_id && p2.time < p.time){    // The "less than" is crucial here. I am assuming that the prob.
																			  // of future events does not influence the prob. of current or past events
										System.out.println("Test Dependency is: " + d_id);
										
										rawProb *= p2.prob;		// Multiply 
									
									}
								
								}
								*/
								System.out.println("Kind of Worked");
								if(e.time > p.time){
									System.out.println("Worked a little better");
									e.updateProb(p.prob); 		// Multiply 
								}
								
							}
							
						}
						
						
					}
					
					
					
					
				}
				
				
				
				
				
				System.out.println("\nEvent Summary\n");
				
				for(prob_obj finalProb: arrayProb){
					
					Integer thisId= finalProb.id;
					
					for(event_obj finalEvent: thread){
						
						
						if(finalEvent.id == thisId){
							
							if(!thread.isEmpty()){
								

								
								System.out.print("{[id=" + finalEvent.id + "],");	
									System.out.print("[p=" + finalEvent.prob + "],");					
									System.out.print("[t=" + finalEvent.time + "],[");
									int sCount = 1;
									for(String s: finalEvent.subject){
										if(sCount != finalEvent.subject.size())
											System.out.print(s + ",");
										else
											System.out.print(s + "],[");
										sCount++;
									}
									int rCount = 1;
									for(String r: finalEvent.relation){
										if(rCount != finalEvent.relation.size())
											System.out.print(r + ",");
										else
											System.out.print(r + "],[");
										rCount++;
									}
									int cCount = 1;
									for(String c: finalEvent.concept){
										if(cCount != finalEvent.concept.size())
											System.out.print(c + ",");
										else
											System.out.print(c + "],[");
										cCount++;
									}
									int dCount = 1;
									for(Integer d: finalEvent.dep){
										if(dCount != finalEvent.dep.size())
											System.out.print(d + ",");
										else
											System.out.print(d + "]}");
										dCount++;
									}
									System.out.print("\n");
									
								
								
								
							}else{
								
								System.out.println("Event Thread Empty");
								
							}
							
							
							
							
						}
						
						
						
					}
					
					
					
				}
				
				
				for(event_obj e: thread){
					
					
					for(prob_obj p: arrayProb){
						
						if(p.id == e.id)
							e.setProb(p.prob);
						
						
					}
					
					
					
					
				}
				
				
				
				
				
				home_trig = 0;
				break;
			
				
				
				
				
			case 3:
				thread = new ArrayList<event_obj>();
				arrayProb = new ArrayList<prob_obj>();
				home_trig = 0;
				id = 0;
				break;
		}
		
		}
		sc.close(); 
		
		
		
		
		
	}

}
