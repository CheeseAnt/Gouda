package com.example.anton.backroundyoutube;

import android.content.Context;
import android.content.res.AssetManager;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * Created by Anton on 07/06/2017.
 */

public class JSONMenuReader {

    Context context;
    String JSONStream;

    public JSONMenuReader(Context context) {
        this.context = context;

        JSONStream = readJSON(context);
    }

    // to read JSON into stream
    private String readJSON(Context context) {
        String total = "", line;

        try {
            AssetManager aManage = context.getAssets(); // open relevant file
            InputStream instr = aManage.open("menu.json");

            if (instr != null) {
                InputStreamReader reader = new InputStreamReader(instr);
                BufferedReader buffreader = new BufferedReader(reader); // readers

                try {
                    while ((line = buffreader.readLine()) != null) {
                        total = total + line; // combine file
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
        catch(Exception e) {
            e.printStackTrace();
        }

        return total; // return stream
    }

    public ArrayList<String> getCategories() {
        ArrayList<String> categories = new ArrayList<>();
        try { // open json stream
            JSONObject jsonRoot = new JSONObject(JSONStream);

            Iterator<String> catKeys = jsonRoot.keys(); // find keys within

            while (catKeys.hasNext()) {
                categories.add(catKeys.next());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return categories;
    }

    public ArrayList<String> getSubCategories(ArrayList<String> parentTree) {
        ArrayList<String> subCats = new ArrayList<>();

        try { // open json stream
            JSONObject jsonRoot = new JSONObject(JSONStream);

            JSONArray items = jsonRoot.getJSONArray(parentTree.get(0));
            JSONArray parents;

            int a;

            for(int i = 0; i < items.length(); i++) {
                parents = items.getJSONObject(i).getJSONArray("parents");
                for(a = 0; a < parentTree.size() - 1; a++) {
                    if(!parents.get(a).toString().equalsIgnoreCase(parentTree.get(a + 1)))
                        break;
                }
                if(a == (parentTree.size() - 1))
                    if((parents.length() > (parentTree.size() - 1)) && isNotPresent(subCats, parents.get(a).toString()))
                        subCats.add(parents.get(a).toString());
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        if(subCats.size() > 0)
            return subCats;
        else
            return null;
    }

    public boolean isNotPresent(ArrayList<String> original, String incoming) {
        for(int i = 0; i < original.size(); i++)
            if(original.get(i).equalsIgnoreCase(incoming))
                return false;

        return true;
    }

    public ArrayList<String> getDetail(ArrayList<String> parentTree, String detail) {
        ArrayList<String> data = new ArrayList<>();

        try { // open json stream
            JSONObject jsonRoot = new JSONObject(JSONStream);

            JSONArray items = jsonRoot.getJSONArray(parentTree.get(0));
            JSONArray parents;

            int a;

            for(int i = 0; i < items.length(); i++) {
                parents = items.getJSONObject(i).getJSONArray("parents");
                for(a = 0; a < parentTree.size() - 1; a++) {
                    if(!parents.get(a).toString().equalsIgnoreCase(parentTree.get(a + 1)))
                        break;
                }
                if(a == (parentTree.size() - 1))
                    data.add(items.getJSONObject(i).getString(detail));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        if(data.size() > 0)
            return data;
        else
            return null;
    }

}
