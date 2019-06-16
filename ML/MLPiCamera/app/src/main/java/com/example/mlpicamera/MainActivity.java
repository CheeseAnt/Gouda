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

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.FileProvider;

import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.widget.Button;
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
import java.util.Locale;

public class MainActivity extends AppCompatActivity {
    private static final int req_code = 100;
    private ImageView image_photo;
    private static File temp_file;
    private static final String tempFileName = "inferenceImage";
    private static final String baseURL = "http://x.x.x.x:5000/";
    private static final String flaskPOSTURL = baseURL + "infer";
    private TextView object_name;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        //  check for permissions
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[] {Manifest.permission.CAMERA}, 0);
        }

        // set layout and find view items
        setContentView(R.layout.activity_main);
        Button take_photo = findViewById(R.id.take_photo);
        image_photo = findViewById(R.id.image_photo);
        object_name = findViewById(R.id.object_name);

        // automatically resize the text
        object_name.setAutoSizeTextTypeWithDefaults(TextView.AUTO_SIZE_TEXT_TYPE_UNIFORM);

        // create temporary file which will be used for transfer
        try {
            temp_file = File.createTempFile(tempFileName, ".jpg", getExternalFilesDir(Environment.DIRECTORY_PICTURES));
        }
        catch (IOException ex) {
            ex.printStackTrace();
            System.out.println("Couldn't dedicate temporary storage to file.");
            temp_file = null;
        }

        // set the on click for the picture taking
        take_photo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(temp_file != null) {
                    Intent cInt = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

                    // let the photo be saved to memory, otherwise it comes out as low res
                    Uri photoURI = FileProvider.getUriForFile(MainActivity.this,
                            "com.example.mlpicamera.provider", temp_file);
                    cInt.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                    startActivityForResult(cInt, req_code);
                }
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        // when the picture has finished being taken
        if (requestCode == req_code) {
            if (resultCode == RESULT_OK) {
                // rotate first by 90 degrees as default rotates it
                Matrix m  = new Matrix();
                m.postRotate(90);

                // create the bitmap from the temporary file
                BitmapFactory.Options bmOptions = new BitmapFactory.Options();
                Bitmap temp_bm = BitmapFactory.decodeFile(temp_file.getAbsolutePath(), bmOptions);
                temp_bm = Bitmap.createBitmap(temp_bm, 0, 0, temp_bm.getWidth(), temp_bm.getHeight(),
                        m, true);

                // display the image on screen and begin the POST request to the server
                image_photo.setImageBitmap(temp_bm);
                postRequest(temp_bm);

                // delete the temporary file
                temp_file.delete();
            } else if (resultCode == RESULT_CANCELED) {
                Toast.makeText(this, "Cancelled", Toast.LENGTH_LONG).show();
            }
        }
    }

    /**
     * Gets a base64 encoded version of the image
     * @param bmp input image
     * @return base64 encoded string
     */
    public String getStringImage(Bitmap bmp){
        ByteArrayOutputStream baos = new ByteArrayOutputStream();

        // compress the image a decent amount as it will be resized for inference anyway
        bmp.compress(Bitmap.CompressFormat.JPEG, 25, baos);
        byte[] imageBytes = baos.toByteArray();
        return Base64.encodeToString(imageBytes, Base64.NO_WRAP);
    }

    /**
     * POST the request using an async task
     * @param bm inference image
     */
    public void postRequest(Bitmap bm) {
        new PostFile().execute(bm);
    }

    /**
     * Class that extends ASyncTask to perform network transfer
     */
    private class PostFile extends AsyncTask<Bitmap, Integer, Long> {
        private String object;
        private String accuracy;

        @Override
        protected Long doInBackground(Bitmap... bms) {
            HttpURLConnection client = null;
            try {
                // create connection with the server
                URL url = new URL(flaskPOSTURL);
                client = (HttpURLConnection) url.openConnection();

                // perform a POST request
                client.setRequestMethod("POST");
                client.setDoOutput(true);

                // get the encoded image and replace special characters to avoid corruption
                OutputStream outPost = new BufferedOutputStream(client.getOutputStream());
                String encodedImage = getStringImage(bms[0]).replace("=", "@")
                        .replace("+", "*");

                // transfer and close stream
                outPost.write(encodedImage.getBytes());
                outPost.flush();
                outPost.close();

                // once the transfer was successful, obtain the prediction results
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
                // disconnect client at the end
                if(client != null)
                    client.disconnect();
            }
            return null;
        }

        @Override
        protected void onPostExecute(Long aLong) {
            super.onPostExecute(aLong);

            // display the results of the inference in a textview
            String disp =  "%s: %.4f";

            try {
                object_name.setText(String.format(Locale.ENGLISH, disp, object.split(",")[0],
                        Double.parseDouble(accuracy)));
            }
            catch (NumberFormatException nfex) {
                nfex.printStackTrace();
                object_name.setText("Error processing accuracy");
            }
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();

            // show a pending text
            object_name.setText("Sending POST Request...");
        }
    }
}
