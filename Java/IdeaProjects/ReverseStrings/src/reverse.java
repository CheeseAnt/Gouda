import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

/**
 * Reads n lines of strings, reversing the strings within each line
 * Created by Anton on 22/04/2017.
 */
public class reverse {
    public static void main(String [] args) throws IOException {
        // declare reader
        BufferedReader read = new BufferedReader(new InputStreamReader(System.in));

        // make a list of list of strings
        ArrayList<ArrayList<String>> rev_string = new ArrayList<ArrayList<String>>();

        // read amount of lines to read
        int n_lines = Integer.parseInt(read.readLine());

        for(int i = 0; i < n_lines; i++) { // begin reading each line
            String all_lines = read.readLine();
            String [] line = all_lines.split("\\s"); // split along the spaces
            rev_string.add(new ArrayList<String>()); // add the string list in first element of list

            for(int j = line.length-1; j >= 0; j--) {
                rev_string.get(i).add(line[j]); // save in reversed order
            }
        }

        for(int i = 0; i < rev_string.size(); i++)
            for (int j = 0; j < rev_string.get(i).size(); j++) { // print in normal order
                if (j != (rev_string.get(i).size() - 1))
                    System.out.print(rev_string.get(i).get(j) + " ");

                else if (i != (rev_string.size()-1)) // formatting depending on the edge of line/total lines
                    System.out.println(rev_string.get(i).get(j));

                else
                    System.out.print(rev_string.get(i).get(j));
            }
    }
}
