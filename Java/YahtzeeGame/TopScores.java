/*
 * File: TopScores.java
 * ------------------
 * This program will read the top players information from the text file: TopScores.text and have two
 * public methods which will store the names and scores of the top records into two arrays (one is 
 * the score array and the other is the name array which will be used by the ExtendedYahtzee class
 * during the game.
 */

import acm.program.*;
import acm.util.*;

import java.io.*;
import java.util.*;

public class TopScores {
	public TopScores() {
		try {
			BufferedReader rd = new BufferedReader(new FileReader("TopScores.txt"));
			records = new ArrayList<String>();
			while(true) {				
			String list = rd.readLine();
			if (list == null) break;
			records.add(list);
			}
			rd.close();
		} catch (IOException ex) {
			throw new ErrorException(ex);
		}
		
	}
	
	public String[] getNamesArray() {
		String[] result = new String[TOPMAXPLAYERS];
		for(int i = 0; i < records.size()/2; i++) {
			result[i] = records.get(2 * i);
		}
		return result;
	}
	
	public int[] getScoresArray() {
		int[] result = new int[TOPMAXPLAYERS];
		for(int i = 0; i < records.size()/2; i++) {
			result[i] = Integer.parseInt(records.get(2 * i + 1));
		}
		return result;
	}
	
	
	
	
	/**Private instant variables*/
	private ArrayList<String> records;
	
	/**Private constants*/
	private static final int TOPMAXPLAYERS = 10; 
}	
