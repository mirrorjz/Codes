/*
 * File: ExtendedYahtzee.java
 * ------------------
 * This program will print out the top players's names and scores in the IO console, then play the 
 * Yahtzee game with a bonus when the player gets additional Yahtzees and finally save the new top 
 * scores in the corresponding text file.
 */

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import acm.io.*;
import acm.program.*;
import acm.util.*;
import acm.graphics.*;

public class ExtendedYahtzee extends GraphicsProgram implements YahtzeeConstants {
	
	public static void main(String[] args) {
		new ExtendedYahtzee().start(args);
	}
	
		
	public void run() {
		IODialog dialog = getDialog();
		nPlayers = dialog.readInt("Enter number of players");
		playerNames = new String[nPlayers];
		for (int i = 1; i <= nPlayers; i++) {
			playerNames[i - 1] = dialog.readLine("Enter name for player " + i);
		}
		display = new YahtzeeDisplay(getGCanvas(), playerNames);
		printOutTopScores();
		playGame();
		updateTopScores();
	}
	
	/**Print out the previous top scores, the maximum top score is ten if more than ten people have
	 * played the game.*/
	private void printOutTopScores() {
		topScore = new TopScores();
		topScores = topScore.getScoresArray();
		topPlayerNames = topScore.getNamesArray();
		//IODialog dialog = getDialog();
		IOConsole console = getConsole();
		//dialog.println("Top scores:");
		console.println("Top scores:");
		for(int i = 0; i < TOPMAXPLAYERS; i++) {
			if (topScores[i] != 0) {
				String str = topPlayerNames[i] + ": " + topScores[i];
				//dialog.println(str);
				console.println(str);
			}	
		}
	}

	private void playGame() {
		dice = new int[N_DICE];
		initScoreCard();
		for (int i = 0; i < N_SCORING_CATEGORIES; i++) {
			for (int j = 1; j <= nPlayers; j++) {
				display.printMessage(playerNames[j-1] + "'s turn! Click \"Roll Dice\" button to " +
						"roll the dice.");
				display.waitForPlayerToClickRoll(j);
				rollDice();				
				rerollDice();
				chooseCategory(j);
				updateScore(j);	
						
			}		
		}
			
		showGameResult();
		/* You fill this in */
	}
	
	private void rollDice() {
		for (int i = 0; i < N_DICE; i++) {
			dice[i] = rgen.nextInt(1,6);
		}
		display.displayDice(dice);		
	}
	
	private void rerollDice() {
		for (int i = 0; i < 2; i++) {
			display.printMessage("Select the dice you wish to re-roll and click \"Roll Again\".");
			display.waitForPlayerToSelectDice();
			for (int j = 0; j < N_DICE; j++) {
				if (display.isDieSelected(j)) {
					dice[j] = rgen.nextInt(1,6);
				}
			}
			display.displayDice(dice);
		}
	}
	
	
	private void initScoreCard() {
		scorecard = new int[N_CATEGORIES][nPlayers];
		for (int i = 0; i < N_CATEGORIES; i++) {
			for (int j = 1; j <= nPlayers; j++) {
				scorecard[i][j - 1] = -1;
			}
		}
		
	}
	
	private void chooseCategory(int player) {
		boolean isAdditionalYahtzee = checkCategory(YAHTZEE);
		if (isAdditionalYahtzee && scorecard[YAHTZEE - 1][player - 1] == 50) {
			scorecard[TOTAL - 1][player - 1] += BONUS;
			display.updateScorecard(TOTAL, player, scorecard[TOTAL - 1][player - 1]);
			display.printMessage("You get a bonus of 100 for another Yahtzee!! " +
					"Select a category for this roll.");
			// This gives the player bonus of additional Yahtzee.
		} else {
			display.printMessage("Select a category for this roll.");
		}		
		category = display.waitForPlayerToSelectCategory();	
		while (scorecard[category - 1][player - 1] != -1) {
			display.printMessage("Sorry, you've already used that category. Select another.");
			category = display.waitForPlayerToSelectCategory();	
		}
	}
	
	private void updateScore(int player) {
		boolean p = checkCategory(category);
	    if (p) {	
	    	scorecard[category - 1][player - 1] = calculateScore(category);
	    	if (scorecard[TOTAL - 1][player - 1] == -1) {
	    		scorecard[TOTAL - 1][player - 1] = calculateScore(category);
	    	} else {
	    		scorecard[TOTAL - 1][player - 1] += calculateScore(category);
	    	}
	    } else {
	    	scorecard[category - 1][player - 1] = 0;
	    	if (scorecard[TOTAL - 1][player - 1] == -1) {
	    		scorecard[TOTAL - 1][player - 1] = 0;
	    	}
	    }
		display.updateScorecard(category, player, scorecard[category - 1][player - 1]);
		display.updateScorecard(TOTAL, player, scorecard[TOTAL - 1][player - 1]);
	}
	
	private int calculateScore(int category) {
		int score = 0;
		if (category >= ONES && category <= SIXES) {
			for (int i = 0; i < N_DICE; i++) {
				if(dice[i] == category) {
					score += dice[i];
				}
			}
		}
		if (category == THREE_OF_A_KIND || category == FOUR_OF_A_KIND || category == CHANCE) {
			for (int i = 0; i < N_DICE; i++) {
				score += dice[i];
			}
		}
		if (category == FULL_HOUSE) score = 25;
		if (category == SMALL_STRAIGHT) score = 30;
		if (category == LARGE_STRAIGHT) score = 40;
		if (category == YAHTZEE) score = 50;
		return score;
	}
	
	private boolean checkCategory(int category) {
		boolean p = false;
		if ((category >= ONES && category <= SIXES) || category == CHANCE) p = true;
		if (category == THREE_OF_A_KIND) {
			if(testNumOfSameValue(3) ||testNumOfSameValue(4) || testNumOfSameValue(5)) {
				p = true;
			} 
		}	
		if (category == FOUR_OF_A_KIND) {
			if(testNumOfSameValue(4) || testNumOfSameValue(5)) {
				p = true;
			} 
		}
		if (category == FULL_HOUSE) {
			if(testNumOfSameValue(3) && testNumOfSameValue(2)) {
				p = true;
			} 
		}	
		if (category == SMALL_STRAIGHT) {
			if (isSmallStraight()) {
				p = true;
			}
		}	
		if (category == LARGE_STRAIGHT)	{
			if (isLargeStraight()) {
				p = true;
			}
		}
		if (category == YAHTZEE) {
			if (testNumOfSameValue(5)) p = true;
		}
	    return p;
	}
	
	private boolean testNumOfSameValue(int value) {
		boolean p = false;
		int[] numOfSameValue = new int[N_DICE]; //The ith value in this array shows how many dices 
		//share the same value with ith dice (including itself);
		for (int i = 0; i < N_DICE; i++) {
			for (int j = 0; j< N_DICE; j++) {
				if (dice[i] == dice [j]) {
					numOfSameValue[i]++;
				}
			}
		}
		if (arrayContains(numOfSameValue, value)) p = true;
		return p;
	}
	
	private boolean arrayContains(int[] array, int value) {
		int i = 0;
		boolean p = false;
		while ( (i < array.length) && (p == false)) {
			if (array[i] == value) p = true;
			i++;
		}
		return p;
	}
	
	private boolean isSmallStraight() {
		boolean p = false;
		int i = 1;
		while ((i <= 3) && (p == false)) {
			if (arrayContains(dice, i) && arrayContains(dice, i + 1) && arrayContains(dice, i + 2) && 
					arrayContains(dice, i + 3)) {
				p = true;
			}
			i++;
		}
        return p;
	}
	
	private boolean isLargeStraight() {
		boolean p = false;
		int i = 0;
		while ((i <= 2) && (p == false)) {
			if (arrayContains(dice, i) && arrayContains(dice, i + 1) && arrayContains(dice, i + 2) && 
					arrayContains(dice, i + 3) && arrayContains(dice, i + 4)) {
				p = true;
			}
			i++;
		}
        return p;
	}
	
	private void showGameResult() {
		showOtherScores();
		updateTotalScore();
		printWinnerMessage();		
	}
	
	private void showOtherScores() {		
		for (int i = 1; i <= nPlayers; i++) {
			for (int j = ONES; j <= SIXES; j++) {
				scorecard[UPPER_SCORE - 1][i - 1] += scorecard[j - 1][i - 1];
			}
			if (scorecard[UPPER_SCORE - 1][i - 1] >= 63) {
				scorecard[UPPER_BONUS - 1][i - 1] = 35;
			} else {
				scorecard[UPPER_BONUS - 1][i - 1] = 0;
			}
			display.updateScorecard(UPPER_SCORE, i, scorecard[UPPER_SCORE - 1][i - 1] + 1);
			// Add 1 because the initialization value is -1.
			display.updateScorecard(UPPER_BONUS, i, scorecard[UPPER_BONUS - 1][i - 1]);
			for (int j = THREE_OF_A_KIND; j <= CHANCE; j++) {
				scorecard[LOWER_SCORE - 1][i - 1] += scorecard[j - 1][i - 1];
			}
			display.updateScorecard(LOWER_SCORE, i, scorecard[LOWER_SCORE - 1][i - 1] + 1);
			// Add 1 because the initialization value is -1.
		}
	}
	
	private void updateTotalScore() {
		for (int i = 1; i <= nPlayers; i++) {
			scorecard[TOTAL - 1][i - 1] += scorecard[UPPER_BONUS - 1][i - 1];
			display.updateScorecard(TOTAL, i, scorecard[TOTAL - 1][i - 1]);			
		}		
	}
	
	private void printWinnerMessage() {
		int winner = 0;
		for (int i = 1; i <= nPlayers - 1; i++) {
			if (scorecard[TOTAL - 1][winner] < scorecard[TOTAL - 1][i]) {
				winner = i;
			}	
		}
		display.printMessage("Congratulations, " + playerNames[winner] + ", you're the winner with a"
				+ " total score of " + scorecard[TOTAL - 1][winner] + "!");
	}
	
	private void updateTopScores() {
		sequenceCandidates();
		changeTopScores();
		writeToFile();
	}
	
	/**Copy the names and the total scores of the players in the current game and sequence them from
	 * highest score to lowest*/
	private void sequenceCandidates() {
		candidateNames = playerNames;
		candidateScores = new int[nPlayers];
		for(int i = 0; i < nPlayers; i ++) {
			candidateScores[i] = scorecard[TOTAL - 1][i];
		}
		int maxScoreIndex = 0;
		for(int j = 0; j < nPlayers - 1; j++) {
			maxScoreIndex = j;
			for(int m = j + 1; m < nPlayers; m++) {
				if(candidateScores[maxScoreIndex] < candidateScores[m]) {
					maxScoreIndex = m;
				}
				String tempName = candidateNames[j];
				candidateNames[j] = candidateNames[maxScoreIndex];
				candidateNames[maxScoreIndex] = tempName;
				
				int tempScore = candidateScores[j];
				candidateScores[j] = candidateScores[maxScoreIndex];
				candidateScores[maxScoreIndex] = tempScore;
			}
		}
		
		
	}
	
	/**Compare the scores from the highest to lowest of the current players to the top ten scores,
	 * and update the score if they are higher than the records.*/
	private void changeTopScores() {
		IOConsole console = getConsole();
		boolean p = false;
		for(int i = 0; i < nPlayers; i ++) {
			for(int j = TOPMAXPLAYERS - 1; j >= 0; j--) {
				if(candidateScores[i] > topScores[j] && p == false) {
					if(j == 0 || topScores[j - 1] != 0) { //This deals the situation that the number 
						//of top scores on the top players list is less than 10. 
						topScores[j] = candidateScores[i];
						topPlayerNames[j] = playerNames[i];
						p = true;
					}	
				}				
			}
			if(p == true) {
				//IODialog dialog = getDialog();
				console.println("Congratulations, " + candidateNames[i] + ", you become one of the " +
						"top " + "ten" + " players now!"); //Congratulates the players who entered the
				//top ten scores in the console program;
			}
			p = false;	
		}
	} 
	
	private void writeToFile() {
		try {
			PrintWriter wr = new PrintWriter(new FileWriter("TopScores.txt"));
			for(int i = 0; i < TOPMAXPLAYERS; i++) {
				if(topScores[i] != 0) {
					wr.println(topPlayerNames[i]);
					wr.println(topScores[i]);
				}
			}
			wr.close();
			} catch (IOException ex) {
				throw new ErrorException(ex);
			}
	}
 	
	
		
/* Private instance variables */
	private TopScores topScore;
	private int nPlayers;
	private String[] playerNames;
	private YahtzeeDisplay display;
	private RandomGenerator rgen = new RandomGenerator();
	private int[] dice;
	private int[][] scorecard;
	private int category;
	private int[] topScores;
	private String[] topPlayerNames;
	private String[] candidateNames;
	private int[] candidateScores;



/* Private constant for the an additional Yahtzee the player rolls*/	
	private static final int BONUS = 100;
	private static final int TOPMAXPLAYERS = 10;
	//private static final double Y_OFFSET = 15;

}

