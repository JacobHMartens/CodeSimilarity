// Arup Guha
// 2/26/08
// Solves the Eight Queens problem using backtracking.
// Ported to Java on 7/25/2010

public class EightQueens {

	private int[] perm;
	private boolean[] used;
	private int numsols;
	
	public static void main(String[] args) {
    	EightQueens obj = new EightQueens(5);
    	obj.solveIt();
    	obj.printNumSols();
	}
	
	// Creates an EightQueens object for an nxn board.
	public EightQueens(int n) {
		
		perm = new int[n];
		used = new boolean[n];
		numsols = 0;
		
		for (int i=0; i<n; i++) {
			perm[i] = -1;
			used[i] = false;
		}
	}

	// Solves the 8-Queens problem for this object. This is just a 
	// wrapper function.
	public void solveIt() {
          
     	// Call the recursive function.
     	solveItRec(0);
	}

	// Pre-condition: perm stores a permutation of queens from index 0 to location-1
	//                that is valid for a set of location number of non-conflicting
	//                queens. location represents the column we are placing the next
	//                queen, and usedList keeps track of the rows in which queens
	//                have already been placed.
	public void solveItRec(int location) {
     
    	int i;
    
    	// We've found a solution to the problem, so print it!
    	if (location == perm.length) {
        	printSol();
        	numsols++;
    	}
    
    	// Loop through possible locations for the next queen to place.
    	for (i=0; i<perm.length; i++) {
        
        	// Only try this row if it hasn't already been used.
        	if (used[i] == false) {
            
            	// We can actually place this particular queen without conflict!                     
            	if (!conflict(location, i)) {
                                
                	// Place the new queen!                
                	perm[location] = i;
                
                	// We've used this row now, so mark that.
                	used[i] = true;
                
                	// Recursively solve this board.
                	solveItRec(location+1);
                
                	// Unselect this square, so that we can continue trying to
                	// fill it with the next possible choice.
                	used[i] = false;
            	}                         
                                 
        	}    
    	}
     
	} 

	private boolean conflict(int location, int row) {
    
    	int i;
    
    	// See if the grid spot (location, row) shares a diagonal with any of
    	// the previously placed queens.
    	for (i=0; i<location; i++)
    
        	// Diagonals have equal distance in the x and y axes.
        	if (Math.abs(location - i) == Math.abs(perm[i] - row))
            	return true;
            
    	// No conflict, so we could place a queen there.
    	return false;    
	}

	// Prints a two-dimensional representation of the solution stored in perm for
	// the eight queens problem. 
	public void printSol() {
     
    	int i,j;
          
     	System.out.println("Here is a solution:\n");
     
     	// Loop through each row.
     	for (i=0; i<perm.length; i++) {
         
         	// Go through each column in row i.
         	for (j=0; j<perm.length; j++) {
         
             	// This means that the queen in column j resides in row i.
             	if (perm[j] == i)     
                	System.out.print("Q ");
                 
             	// No queen here, so print a blank.
             	else
                	System.out.print("_ ");
         	}
         	System.out.println("\n");
     	}
	}
	
	public void printNumSols() {
		System.out.println("There were "+numsols+" solutions.");
	}
	
}