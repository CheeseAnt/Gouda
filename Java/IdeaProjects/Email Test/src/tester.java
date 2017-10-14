import java.util.HashMap;

public class tester {
    int testNum;
    double testf;
    char testy;

    tester(int n, double a, char ickle) {
        testNum = n;
        testf = a;
        testy = ickle;
    }
    public static void main(String [] args) {
        tester testi = new tester(3, 4.6, 'a');
        System.out.println(testi.testy);

        HashMap<String, Integer> nerds = new HashMap<String, Integer>();
        nerds.put("Anton", 21);
        nerds.put("Sean", 21);
        nerds.put("Liam", 22);
        nerds.put("Paddy", 20);
        nerds.put("Killian", 18);

        for(String nerd:nerds.keySet())
            System.out.println(nerds.get(nerd));
    }
}