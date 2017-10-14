
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.*;

public class API_Request {
    private final String USER_AGENT = "Chrome/41.0.2228.0";
    private final static String TAG = "API_Request";

    public static void main(String[] args) {
        API_Request api = new API_Request();

        String response = api.get();

        JSONObject post_resp = null;

        if(response != null) {
            post_resp = api.parseGET(response);
        }

        if(post_resp != null)
            api.post(post_resp);
    }

    // perform get request
    private String get() {
        String url = "https://candidate.hubteam.com/candidateTest/v2/partners?userKey=20eb95f919b9f651db08f3339260";

        try {
            URL target = new URL(url);
            HttpURLConnection con = (HttpURLConnection) target.openConnection();

            con.setRequestMethod("GET"); // set request to GET

            con.setRequestProperty("User-Agent", USER_AGENT);

            int responseCode = con.getResponseCode();

            log(TAG, "Sent GET, received response code " + responseCode);

            BufferedReader bReader = new BufferedReader(new InputStreamReader(con.getInputStream()));
            StringBuilder sBuilder = new StringBuilder();
            String line;

            while((line = bReader.readLine()) != null) {
                sBuilder.append(line);
            }

            bReader.close();

            log(TAG, "Received Message: " + sBuilder.toString());

            return sBuilder.toString();
        }
        catch (MalformedURLException e) {
            log(TAG, "Unable to connect to supplied URL");
            e.printStackTrace();
        }
        catch (IOException e) {
            log(TAG, "Unable to open connection");

            e.printStackTrace();
        }

        return null;
    }

    // create a post request
    private String post(JSONObject response) {
        String url = "https://candidate.hubteam.com/candidateTest/v2/results?userKey=20eb95f919b9f651db08f3339260";

        try {
            URL target = new URL(url);

            HttpURLConnection con = (HttpURLConnection) target.openConnection();

            con.setDoOutput(true);
            con.setDoInput(true);

            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
            con.setRequestProperty("Accept", "application/json");

            OutputStream oSw = con.getOutputStream();

            log(TAG, "Sending POST with: " + response.toString());

            oSw.write(response.toString().getBytes("UTF-8"));
            oSw.flush();
            oSw.close();

            BufferedReader bReader;
            int responseCode = 0;

            try {
                bReader = new BufferedReader(new InputStreamReader(con.getInputStream()));

                responseCode = con.getResponseCode();
            }
            catch (Exception e) {
                bReader = new BufferedReader(new InputStreamReader(con.getErrorStream()));
            }

            StringBuilder sBuilder = new StringBuilder();
            String line;

            while((line = bReader.readLine()) != null) {
                sBuilder.append(line);
            }

            bReader.close();

            log(TAG, "POST Response code: " + responseCode);

            log(TAG, "Received Message: " + sBuilder.toString());

            return sBuilder.toString();
        }
        catch (Exception e) {
            log(TAG, "Unable to POST data");

            e.printStackTrace();
        }

        return null;
    }

    // where the main logic happens
    private JSONObject parseGET(String response) {
        Map<String, List<JSONObject>> countryMap = new HashMap<>(); // maps to hold partner info
        Map<String, SortedMap<Integer, Integer>> availibilityMap = new HashMap<>();

        try {
            JSONObject root = new JSONObject(response); // parse partners
            JSONArray partners = root.optJSONArray("partners");

            if(partners != null) { // parse each person from list
                for(int i = 0; i < partners.length(); i++) {
                    JSONObject person = partners.optJSONObject(i);

                    if(person != null) { // separate people by country
                        String country = person.optString("country");

                        if(country != null) {
                            if(!countryMap.containsKey(country)) { // put in a new list if not already present
                                countryMap.put(country, new ArrayList<>());
                            }

                            countryMap.get(country).add(person);

                            JSONArray dates = person.optJSONArray("availableDates");

                            if(dates != null) {
                                Set<Integer> dateSet = new TreeSet<>(); // create a set to keep track of dates of partner

                                for(int j = 0; j < dates.length(); j++) { // run through dates
                                    String date = dates.getString(j);

                                    int dayRep = dayRepresentation(date); // create a linear representation of the date

                                    if(dayRep != 0) {
                                        dateSet.add(dayRep);

                                        if(!availibilityMap.containsKey(country)) // create the country if not there already
                                            availibilityMap.put(country, new TreeMap<>());

                                        if(dateSet.contains(dayRep - 1)) { // if we have the previous day (so a pair is made)
                                            if(availibilityMap.get(country).containsKey(dayRep - 1)) // increment just the previous day
                                                availibilityMap.get(country).put(dayRep - 1, availibilityMap.get(country).get(dayRep - 1) + 1);
                                            else
                                                availibilityMap.get(country).put(dayRep - 1, 1);
                                        } else if (dateSet.contains(dayRep + 1)) { // or if we have the next day (again creating a pair)
                                            if(availibilityMap.get(country).containsKey(dayRep)) // increment the current day
                                                availibilityMap.get(country).put(dayRep, availibilityMap.get(country).get(dayRep) + 1);
                                            else
                                                availibilityMap.get(country).put(dayRep, 1);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        catch (Exception e) {
            log(TAG, "Unable to parse JSON");
            e.printStackTrace();
        }

        // small object to make handling the date and attendees easier
        class AvailDate {
            public int date = 0;
            public int people = 0;
        }

        Map<String, AvailDate> pairs = new HashMap<>(); // use a sorted map to make sure we always get the earliest date possible
        JSONObject postResponse = new JSONObject();
        JSONArray countries = new JSONArray();

        for(String country : availibilityMap.keySet()) {
            JSONObject chosenCountry = new JSONObject();
            JSONArray countryAttendees = new JSONArray();
            chosenCountry.put("startDate", JSONObject.NULL); // default is null

            pairs.put(country, new AvailDate());

            try {
                for (int time : availibilityMap.get(country).keySet()) { // find the max number of people for a country
                    if (availibilityMap.get(country).get(time) > pairs.get(country).people) {
                        pairs.get(country).people = availibilityMap.get(country).get(time);

                        pairs.get(country).date = time;
                    }
                }

                log(TAG, "Chosen time: " + pairs.get(country).date + " with " + pairs.get(country).people + " people in " + country);

                // start constructing the response object
                Iterator<JSONObject> pIterator = countryMap.get(country).iterator();

                while(pIterator.hasNext()) {
                    JSONObject person = pIterator.next();
                    JSONArray dates = person.optJSONArray("availableDates");

                    if(dates != null) {
                        boolean bothDays = false; // make a boolean to keep track of people with both days

                        for(int i = 0; i < dates.length(); i++) {
                            String date = dates.optString(i);
                            int dayRep = dayRepresentation(date);
                            if(dayRep == pairs.get(country).date || (dayRep == pairs.get(country).date + 1)) {
                                if(dayRep == pairs.get(country).date)
                                    chosenCountry.put("startDate", date);

                                if(!bothDays) // if first day, set boolean
                                    bothDays = true;
                                else { // else must be second day, add to list
                                    countryAttendees.put(person.optString("email"));

                                    break;
                                }
                            }
                        }
                    }
                }

            }
            catch (Exception e) {
                e.printStackTrace();
            }

            chosenCountry.put("name", country); // fill in rest of object
            chosenCountry.put("attendeeCount", pairs.get(country).people);
            chosenCountry.put("attendees", countryAttendees);
            countries.put(chosenCountry);
        }

        postResponse.put("countries", countries);

        return postResponse;
    }

    // log similar to Log.D of android
    private void log(String tag, String message) {
        SimpleDateFormat date_format = new SimpleDateFormat("dd/MM/yy HH:mm:ss.SSS");
        Date resultdate = new Date(System.currentTimeMillis());
        String time =  date_format.format(resultdate);
        System.out.println(time + " : " + tag + " : " + message);
    }

    // returns the amount of days in a specific month and year
    private int daysInMonth(int month, int year) {
        switch(month) {
            case 1: return 31;
            case 2: if(year%4 == 0) return 29;
            else return 28;
            case 3: return 31;
            case 4: return 30;
            case 5: return 31;
            case 6: return 30;
            case 7: return 31;
            case 8: return 31;
            case 9: return 30;
            case 10: return 31;
            case 11: return 30;
            case 12: return 31;
            default: return 0;
        }
    }

    // returns a day representation of the current date, year independent
    private int dayRepresentation(String date) {
        String[] separated = date.split("-");
        try {
            int year = Integer.parseInt(separated[0]);
            int month = Integer.parseInt(separated[1]);

            int dayRep = 0;

            for(int i = 1; i < month; i++) {
                dayRep += daysInMonth(i, year);
            }

            dayRep += Integer.parseInt(separated[2]);

            return dayRep;
        }
        catch (Exception e) {
            log(TAG, "Unable to parse date from " + date);

            e.printStackTrace();
        }

        return 0;
    }
}
