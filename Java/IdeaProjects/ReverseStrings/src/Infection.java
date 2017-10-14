import java.io.File;
import java.io.FileInputStream;

/**
 * Created by Anton on 28/09/2017.
 */
public class Infection {
    public static void main(String[] args) {
        File f = new File("C:/Users/Anton/Downloads/PracticeInput4.txt");

        String input = null;

        if(f.canRead())
            System.out.println("Can read file");
        else
            System.out.println("Cannot read file");

        try {
            FileInputStream fIs = new FileInputStream(f);

            byte[] bits = new byte[fIs.available()];

            while (fIs.available() > 0) {
                fIs.read(bits);
            }

            fIs.close();

            input = new String(bits);
            System.out.println(input);

            String[] splitString = input.split("\n");

            int counter = 0;

            System.out.println(splitString.length);

            char[][] matr = new char[splitString.length][splitString.length];

            for(int i = 0; i < splitString.length; i++) {
                matr[i] = splitString[i].toCharArray();
            }

            for(int i = 0; i < splitString.length; i++) {
                for(int j = 0; j < splitString.length; j++) {
                        if(matr[i][j] >= 31) {
                            try {
                            matr[i - 1][j - 1] = 31;
                            }
                            catch (Exception e) {
                            }
                        }
                }
            }
            System.out.println(counter);
        }
        catch (Exception e){
            e.printStackTrace();
        }
    }
}
