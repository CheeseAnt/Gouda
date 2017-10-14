import java.io.File;
import java.io.FileInputStream;

/**
 * Created by Anton on 28/09/2017.
 */
public class BoxSelector {
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

            String[] splitString = input.split(";");

            int counter = 0;

            for (String s : splitString) {
                String[] bSplit = s.split(",");

                if(bSplit.length > 1) {
                    double boxd = Double.parseDouble(bSplit[0]);
                    int triSq = Integer.parseInt(bSplit[1]);
                    double prSide = Double.parseDouble(bSplit[2]);

                    switch (triSq) {
                        case 3:
                            if(boxd >= Math.round(prSide/Math.sqrt(3))) {
                            counter++;

                            System.out.println(boxd + " vs " + prSide/Math.sqrt(3));
                        }

                            break;
                        case 4:
                            if((boxd*2) >= Math.round(Math.sqrt((prSide * prSide) + (prSide * prSide)))) {
                                counter++;
                            }

                            break;
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
