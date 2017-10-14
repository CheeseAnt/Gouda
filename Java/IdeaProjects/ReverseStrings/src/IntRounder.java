import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;

/**
 * Created by Anton on 28/09/2017.
 */
public class IntRounder {
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

            input = new String(bits);
            System.out.println(input);

            String[] splitString = input.split(",");

            double num = 0;
            for (String s : splitString) {
                if(s != null)
                    num += Double.parseDouble(s);

                System.out.println(Double.parseDouble(s));
            }

            System.out.println(num);

            System.out.println(Math.round(num/splitString.length));
        }
        catch (Exception e){
            e.printStackTrace();
        }
    }
}
