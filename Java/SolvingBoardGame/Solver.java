/****************************************************************************
 *  Name:         Jing
 *  Compilation:  javac RandomizedQueue.java
 *  Execution:    java RandomizedQueue
 *  Dependencies: StdRandom.java
 *
 *  Description: A immutable data type to solve a Board puzzle.
 ****************************************************************************/

import java.util.Arrays;
import java.util.Iterator;
import java.util.Scanner;

 
public class Solver {
    private MinPQ<SearchNode> initialPQ = new MinPQ<SearchNode>();
    private MinPQ<SearchNode> twinPQ = new MinPQ<SearchNode>();
    //private int minmoves = -1;         // the min of number of moves to solve the puzzle
    //private int iniManhDist;
    //private int twinManhDist;
    private SearchNode iniDequeued;
    private SearchNode twinDequeued;
     
    
    // find a solution to the initial board (using the A* algorithm)
    public Solver(Board initial) {
        SearchNode iniSN = new SearchNode(); 
        SearchNode twinSN = new SearchNode();         // initial search node
        
        // initial the search nodes parameters
        iniSN.prev = null;
        twinSN.prev = null;
        iniSN.nodeBoard = initial;
        twinSN.nodeBoard = initial.twin(); 
        iniSN.steps = 0;
        twinSN.steps = 0;
        iniSN.priority = initial.manhattan();
        //iniManhDist = iniSN.priority;
        twinSN.priority = initial.twin().manhattan();
        //twinManhDist = twinSN.priority;
        
        // initiate the row_0 and col_0 for the search nodes
        String iniStr = initial.toString();
        Scanner iniSC = new Scanner(iniStr);
        int N = iniSC.nextInt();
        // Checkout the location indexes of the empty tile;
        boolean found = false;
        for (int i = 0; i < N; i++) {
             if (found) break;
             for (int j = 0; j < N; j++) {
                 if (iniSC.nextInt() == 0) {
                     iniSN.row_0 = i;
                     iniSN.col_0 = j;
                     found = true;
                     break;
                 }   
             }
         }
         twinSN.row_0 = iniSN.row_0;
         twinSN.col_0 = iniSN.col_0;   
        
         // insert them into the MinPQ        
         initialPQ.insert(iniSN);
         twinPQ.insert(twinSN);
        
         // Dequeued search nodes
         iniDequeued = initialPQ.delMin();    // the search node to be processed
         twinDequeued = twinPQ.delMin();
        
        while ((!iniDequeued.nodeBoard.isGoal()) && (!twinDequeued.nodeBoard.isGoal())) {
            insertNode(iniDequeued, initialPQ);
            insertNode(twinDequeued, twinPQ);
            //minimoves
            iniDequeued = initialPQ.delMin();
            twinDequeued = twinPQ.delMin();              
        }        
    }
    
    /** The SearchNode class includes the Board, the priority number, the previous search 
     * node, the steps that have moved as well as two int numbers (row_0 and col_0) that 
     * show where is the empty tile. 
     */
    private class SearchNode implements Comparable<SearchNode> {
        private Board nodeBoard;
        private int priority;
        private SearchNode prev;          // refer to the previous searchNode
        private int steps;                // number of moves from initial to this node
        private int row_0;
        private int col_0;
        public int compareTo(SearchNode that) {
            if (this.priority < that.priority) return -1;
            if (this.priority > that.priority) return +1;
            if (this.priority == that.priority) {
                if (this.nodeBoard.hamming() < that.nodeBoard.hamming()) return -1;
                if (this.nodeBoard.hamming() > that.nodeBoard.hamming()) return +1;
            }
            return 0;
        }
    }
    
    //exchange a[r1][col] and a[r2][col] 
    private static void exchcol(int[][] a, int r1, int r2, int col) {
        int swap = a[r1][col];
        a[r1][col] = a[r2][col];
        a[r2][col] = swap;
    }     
    
    // exchange a[i] and a[j]
    private static void exch(int[] a, int i, int j) {
        int swap = a[i];
        a[i] = a[j];
        a[j] = swap;
    }

    // Given the dequeued searchNode x, insert the valid neighbors into the PQ;
    private void insertNode(SearchNode x, MinPQ<SearchNode> pq) {
        // Get the matrix of the blocks and construct neighbors to insert
        String xboardS = x.nodeBoard.toString();
        Scanner xSC = new Scanner(xboardS);       
        int N = xSC.nextInt();    
        int[][] tiles = new int[N][N];
        for (int i = 0; i < N; i++) {
             for (int j = 0; j < N; j++) {
                 tiles[i][j] = xSC.nextInt();   
             }
        } 
                
        // Switch with the upper row element
        if (x.row_0 != 0 && (x.prev == null || (x.prev.row_0 != x.row_0 - 1))){
            exchcol(tiles, x.row_0, x.row_0 -1, x.col_0);
            Board neighbor = new Board(tiles);
            SearchNode nextNode = new SearchNode();
            nextNode.nodeBoard = neighbor;
            nextNode.row_0 = x.row_0 - 1;
            nextNode.col_0 = x.col_0;
            nextNode.steps = x.steps + 1;
            nextNode.prev = x;
            if (tiles[x.row_0][x.col_0] == N*(x.row_0) + x.col_0) {
                nextNode.priority = x.priority;
            } else if (tiles[x.row_0][x.col_0] == N*(x.row_0 - 1) + x.col_0) {
                nextNode.priority = x.priority + 2;
            } else { nextNode.priority = x.priority + 1; }
            pq.insert(nextNode);    // insert the search node to the PQ
            
            // return the matrix of tiles to the original position
            exchcol(tiles, x.row_0, x.row_0 -1, x.col_0);
        }
        
        // Switch with the lower row element    
        if (x.row_0 != (N - 1) && ((x.prev == null) || (x.prev.row_0 != x.row_0 + 1))) {
            exchcol(tiles, x.row_0, x.row_0 + 1, x.col_0);
            Board neighbor = new Board(tiles);
            SearchNode nextNode = new SearchNode();
            nextNode.nodeBoard = neighbor;
            nextNode.row_0 = x.row_0 + 1;
            nextNode.col_0 = x.col_0;
            nextNode.steps = x.steps + 1;
            nextNode.prev = x;
            if (tiles[x.row_0][x.col_0] == N*(x.row_0) + x.col_0) {
                nextNode.priority = x.priority;
            } else if (tiles[x.row_0][x.col_0] == N*(x.row_0 + 1) + x.col_0) {
                nextNode.priority = x.priority + 2;
            } else { nextNode.priority = x.priority + 1; }
            pq.insert(nextNode);    // insert the search node to the PQ
            
            // return the matrix of tiles to the original position
            exchcol(tiles, x.row_0, x.row_0 +1, x.col_0);
        }
        
        // Switch with the left element  
        if (x.col_0 != 0 && (x.prev == null || (x.prev.col_0 != x.col_0 - 1))){
            exch(tiles[x.row_0], x.col_0, x.col_0 -1);
            Board neighbor = new Board(tiles);
            SearchNode nextNode = new SearchNode();
            nextNode.nodeBoard = neighbor;
            nextNode.row_0 = x.row_0;
            nextNode.col_0 = x.col_0 - 1;
            nextNode.steps = x.steps + 1;
            nextNode.prev = x;
            if (tiles[x.row_0][x.col_0] == N*(x.row_0) + x.col_0) {
                nextNode.priority = x.priority;
            } else if (tiles[x.row_0][x.col_0] == N*x.row_0 + x.col_0 - 1) {
                nextNode.priority = x.priority + 2;
            } else { nextNode.priority = x.priority + 1; }
            pq.insert(nextNode);    // insert the search node to the PQ
            
            // return the matrix of tiles to the original position
            exch(tiles[x.row_0], x.col_0, x.col_0 -1);
        }
        
        // Switch with the right element
        if (x.col_0 != N - 1 && (x.prev == null || (x.prev.col_0 != x.col_0 + 1))){
            exch(tiles[x.row_0], x.col_0, x.col_0 +1);
            Board neighbor = new Board(tiles);
            SearchNode nextNode = new SearchNode();
            nextNode.nodeBoard = neighbor;
            nextNode.row_0 = x.row_0;
            nextNode.col_0 = x.col_0 + 1;
            nextNode.steps = x.steps + 1;
            nextNode.prev = x;
            if (tiles[x.row_0][x.col_0] == N*(x.row_0) + x.col_0) {
                nextNode.priority = x.priority;
            } else if (tiles[x.row_0][x.col_0] == N*x.row_0 + x.col_0 + 1) {
                nextNode.priority = x.priority + 2;
            } else { nextNode.priority = x.priority + 1; }
            pq.insert(nextNode);    // insert the search node to the PQ
            
            // return the matrix of tiles to the original position
            exch(tiles[x.row_0], x.col_0, x.col_0 +1);
        }        
    }
    
    // is the initial board solvable?    
    public boolean isSolvable() {
        return iniDequeued.nodeBoard.isGoal();
    }
    
    // min number of moves to solve initial board; -1 if unsolvable
    public int moves() {
        if (isSolvable()) {
            return iniDequeued.steps;
        } else { return -1; }
    }
    
    // sequence of boards in a shortest solution; null if unsolvable
    public Iterable<Board> solution() {
        if (isSolvable()) {
            Stack<Board> solution = new Stack<Board>();
            SearchNode item = iniDequeued;
            while (item!= null) {
                solution.push(item.nodeBoard);
                item = item.prev;
            } 
            return solution;
        }
        return null;    
    }
    
    // solve a slider puzzle (given below)
    public static void main(String[] args) {
         // create initial board from file
         In in = new In(args[0]);
         int N = in.readInt();
         int[][] blocks = new int[N][N];
         for (int i = 0; i < N; i++)
             for (int j = 0; j < N; j++)
                 blocks[i][j] = in.readInt();
         Board initial = new Board(blocks);
         
         // solve the puzzle
         Solver solver = new Solver(initial);
         
         // print solution to standard output
         if (!solver.isSolvable())
             StdOut.println("No solution possible");
         else {
             StdOut.println("Minimum number of moves = " + solver.moves());
             for (Board board : solver.solution())
                 StdOut.println(board);
         } 
    }                  
}



