package com.example.mlpicamera;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;

import com.google.android.material.bottomnavigation.BottomNavigationView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.annotation.NonNull;
import androidx.core.content.FileProvider;

import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.MenuItem;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class MainActivity extends AppCompatActivity {
    private static final int req_code = 100;
    private ImageView image_photo;
    private static File temp_file;
    private static final String tempFileName = "inferenceImage";
    private static final String baseURL = "http://79.97.31.139:5000/";
    private static final String flaskPOSTURL = baseURL + "infer";
    private TextView object_name;

    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = new BottomNavigationView.OnNavigationItemSelectedListener() {

        @Override
        public boolean onNavigationItemSelected(@NonNull MenuItem item) {
            switch (item.getItemId()) {
                case R.id.navigation_home:
                    return true;
                case R.id.navigation_dashboard:
                    if(temp_file != null) {
                        Intent cInt = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                        Uri photoURI = FileProvider.getUriForFile(MainActivity.this, "com.example.mlpicamera.provider", temp_file);
                        cInt.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                        startActivityForResult(cInt, req_code);
                    }
                    return true;
                case R.id.navigation_notifications:
                    return true;
            }
            return false;
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[] {Manifest.permission.CAMERA}, 0);
        }

        setContentView(R.layout.activity_main);
        BottomNavigationView navView = findViewById(R.id.nav_view);
        navView.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
        image_photo = findViewById(R.id.image_photo);
        object_name = findViewById(R.id.object_name);

        try {
            temp_file = File.createTempFile(tempFileName, ".jpg", getExternalFilesDir(Environment.DIRECTORY_PICTURES));
        }
        catch (IOException ex) {
            ex.printStackTrace();
            System.out.println("Couldn't dedicate temporary storage to file.");
            temp_file = null;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == req_code) {
            if (resultCode == RESULT_OK) {
                Matrix m  = new Matrix();
                m.postRotate(90);

                BitmapFactory.Options bmOptions = new BitmapFactory.Options();
                Bitmap temp_bm = BitmapFactory.decodeFile(temp_file.getAbsolutePath(), bmOptions);
                temp_bm = Bitmap.createBitmap(temp_bm, 0, 0, temp_bm.getWidth(), temp_bm.getHeight(),
                        m, true);

                image_photo.setImageBitmap(temp_bm);
                postRequest(temp_bm);

                temp_file.delete();
            } else if (resultCode == RESULT_CANCELED) {
                Toast.makeText(this, "Cancelled", Toast.LENGTH_LONG).show();
            }
        }
    }

    public String getStringImage(Bitmap bmp){
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        bmp.compress(Bitmap.CompressFormat.JPEG, 100, baos);
        byte[] imageBytes = baos.toByteArray();
        return Base64.encodeToString(imageBytes, Base64.NO_WRAP);
    }

    public void postRequest(Bitmap bm) {
        PostFile ps = new PostFile();
        ps.execute(bm);

    }

    private class PostFile extends AsyncTask<Bitmap, Integer, Long> {
        private String object;
        private String accuracy;

        @Override
        protected Long doInBackground(Bitmap... bms) {
            HttpURLConnection client = null;
            try {
                URL url = new URL(flaskPOSTURL);
                client = (HttpURLConnection) url.openConnection();

                client.setRequestMethod("POST");
                client.setDoOutput(true);

                OutputStream outPost = new BufferedOutputStream(client.getOutputStream());
                String encodedImage = getStringImage(bms[0]).replace("=", "@")
                        .replace("+", "*");

                outPost.write(encodedImage.getBytes());
                outPost.flush();
                outPost.close();

                if(client.getResponseCode() == HttpURLConnection.HTTP_OK) {
                    object = client.getHeaderField("prediction");
                    accuracy = client.getHeaderField("accuracy");

                    System.out.println("Object: " + object + " with accuracy " + accuracy);
                }
            }
            catch (MalformedURLException mEx) {
                mEx.printStackTrace();
                System.out.println("Failed to send POST");
            }
            catch (IOException ioEx) {
                ioEx.printStackTrace();
                System.out.println("Failed to open URL Connection");
            }
            finally {
                if(client != null)
                    client.disconnect();
            }
            return null;
        }

        @Override
        protected void onPostExecute(Long aLong) {
            super.onPostExecute(aLong);

            String disp = object.split(",")[0] + " : " + accuracy;
            object_name.setText(disp);
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();

            object_name.setText("Sending POST Request...");
        }
    }
}
