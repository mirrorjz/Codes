/****************************************************************************
 *  Name:         Jing
 *  Compilation:  javac Board.java
 *  Execution:    java Board
 *  Dependencies: 
 *
 *  Description: A immutable data type to describe a Board
 ****************************************************************************/
 
import java.util.Arrays;
import java.util.Iterator;
import java.util.Scanner;

// construct a board from an N-by-N array of blocks
public class Board {
    private int N;               // The dimension of the Board;
    private int[] bblocks;       // The blocks of the Board that contains N^2 elements
    private int total;           // total number of tiles in the Board, including the empty one
     
    // (where blocks[i][j] = block in row i, column j)
    public Board(int[][] blocks) {
        N = blocks.length;
        total = N * N;
        bblocks = new int[total];
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int index = i*N + j;
                bblocks[index] = blocks[i][j];
            }
        }
    }

    // board dimension N
    public int dimension() {return N; }

    // number of blocks out of place
    public int hamming() {
        int result = 0;
        for (int i = 0; i < (total - 1); i++) {
            if (bblocks[i] != (i + 1)) {
                result++;
            }               
        }
        return result;        
    }

    // sum of Manhattan distances between blocks and goal
    public int manhattan() {
        int result = 0;
        for (int i = 0; i < total; i++) {
            if (bblocks[i] != 0) {
                int row = i / N;
                int col = i % N;
                int rowG = (bblocks[i] - 1) / N;      // The row position in the goal board
                int colG = (bblocks[i] - 1) % N; 
                int dist = Math.abs(row - rowG) + Math.abs(col - colG);
                result = result + dist;
            }
        }
        return result;
    }

    // is this board the goal board?
    public boolean isGoal() { return hamming() == 0; }

    // a board that is obtained by exchanging two adjacent blocks in the same row
    public Board twin() {
        int[][] twinblocks = new int[N][N];
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int index = i*N + j;
                twinblocks[i][j] = bblocks[index];
            }    
        }        
        int i = 0;
        while (true) {
           if (bblocks[i] != 0 && bblocks[i+1] != 0 && ((i + 1) % N != 0)) break;
           i++;
        }
        int row = i / N;
        int col = i % N;
        exch(twinblocks[row], col, col + 1);
        Board result = new Board(twinblocks);
        return result;  
    }
    
    // exchange a[i] and a[j]
    private static void exch(int[] a, int i, int j) {
        int swap = a[i];
        a[i] = a[j];
        a[j] = swap;
    }

 

    // does this board equal y?
    public boolean equals(Object y) {
        if (y == this) return true;
        if (y == null) return false;
        if (y.getClass() != this.getClass()) return false;
        Board that = (Board) y;
        String thisBoard = this.toString();
        String thatBoard = that.toString();
        if (!(thisBoard.equals(thatBoard))) return false;
        return true;
    }

    // all neighboring boards
    public Iterable<Board> neighbors() {
        Stack<Board> neighbors = new Stack<Board>();
        int[][] nblocks = new int[N][N];       // define a neighbor block;
        int zero_row = -1;                          // The row index of "0" block
        int zero_col = -1;                          // The column index of "0" block
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                int index = i*N + j;
                nblocks[i][j] = bblocks[index];
                if (bblocks[index] == 0) {
                    zero_row = i;
                    zero_col = j;
                } 
            }
        } 
        // Switch with the upper row element
        if (zero_row != 0){
            exchcol(nblocks, zero_row, zero_row -1, zero_col);
            neighbors.push(new Board(nblocks));
            // return to the original position
            exchcol(nblocks, zero_row, zero_row -1, zero_col);
        }
        // Switch with the lower row element    
        if (zero_row != (N - 1)) {
            exchcol(nblocks, zero_row, zero_row + 1, zero_col);
            neighbors.push(new Board(nblocks));
            exchcol(nblocks, zero_row, zero_row + 1, zero_col);
        }
        // Switch with the left element  
        if (zero_col != 0) {
            exch(nblocks[zero_row], zero_col, zero_col - 1);
            neighbors.push(new Board(nblocks));
            exch(nblocks[zero_row], zero_col, zero_col - 1);                 
        }
        // Switch with the right element
        if (zero_col != N - 1) {
            exch(nblocks[zero_row], zero_col, zero_col + 1);
            neighbors.push(new Board(nblocks));
            exch(nblocks[zero_row], zero_col, zero_col + 1);                 
        }
        return neighbors;
        
    }
    
    //exchange a[r1][col] and a[r2][col] 
    private static void exchcol(int[][] a, int r1, int r2, int col) {
        int swap = a[r1][col];
        a[r1][col] = a[r2][col];
        a[r2][col] = swap; 
    }    

    // string representation of this board (in the output format specified below)
    public String toString() {
        StringBuilder s = new StringBuilder();
         s.append(N + "\n");
         for (int i = 0; i < N; i++) {
             for (int j = 0; j < N; j++) {
                 int index = index = i*N + j;
                 s.append(String.format("%2d ", bblocks[index]));
             }
             s.append("\n");
         }
         return s.toString();
    }
    
    // unit tests (not graded) 
    public static void main(String[] args) {
    // create initial board from file
         In in = new In(args[0]);
         int N = in.readInt();
         int[][] blocks = new int[N][N];
         for (int i = 0; i < N; i++)
             for (int j = 0; j < N; j++)
                 blocks[i][j] = in.readInt();
         Board test = new Board(blocks);
         Board test1 = new Board(blocks); 
         
         StdOut.println(test.toString());
         // Test hamming number
         int hammingNum = test.hamming();
         StdOut.println("The hamming number is " + hammingNum);
         // Test the manhattanNum
         int manhattanNum = test.manhattan();
         StdOut.println("The manhattan number is " + manhattanNum);
         StdOut.println(test.equals(test1));
         
         StdOut.println("The neighbors are:");
         
         Iterable<Board> neighbors = test.neighbors();
         Iterator<Board> iterator = neighbors.iterator();
         while(iterator.hasNext()) {
             Board x = iterator.next();           
             StdOut.println(x);
         }
         
         StdOut.println("The twin Board is: ");
         Board twinB = test.twin();
         StdOut.println(twinB);
         
         blocks[0][0] = blocks[0][1];
         Board test2 = new Board(blocks);
         StdOut.println(test2.equals(test1));
         
         StdOut.println(test.isGoal());
         
         int[] testBlocks = test.bblocks;
         for (int i = 0; i < testBlocks.length; i++) {
             StdOut.println(testBlocks[i]);
         }
         StdOut.println("TestScanner");
         int[][] testTiles = new int[N][N];
         String s = test.toString();
         Scanner sc = new Scanner(s);
         StdOut.println(sc.nextInt());
         
         
         for (int i = 0; i < N; i++) {
             for (int j = 0; j < N; j++) {
                 testTiles[i][j] = sc.nextInt();
                 StdOut.print(testTiles[i][j]);
             }
             StdOut.println();
         }         
         
    
    } 

}