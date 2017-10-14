package com.example.anton.backroundyoutube;

import android.app.Service;
import android.content.Intent;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Bundle;
import android.os.IBinder;
import android.provider.MediaStore;
import android.support.v4.content.LocalBroadcastManager;
import android.util.Log;

/**
 * Created by Anton on 02/06/2017.
 */

public class BackgroundPlayer extends Service {

    final MediaPlayer mPlayer = new MediaPlayer();

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {

        System.out.println("Service Started");
        String vURL;
        int progress;
        Bundle extras = intent.getExtras();

        if (extras != null) {
            if ((vURL = extras.getString("URL")) != null)
                if(vURL.length() > 3) {
                    mPlayer.reset();
                    startVideo(vURL);

                    Log.d("onStart", "starting video");
                }
            try {
                progress = extras.getInt("progress");

                Log.d("Progress", "Being changed: " + Integer.toString(progress));

                mPlayer.seekTo(progress);
            }
            catch (Exception e) {
                e.printStackTrace();
            }

        }
        else {
            Log.d("onStart", "is null");
            String act = intent.getAction();

            if(act != null) {
                Log.d("action", act);
                if (act.equalsIgnoreCase("play"))
                    mPlayer.start();
                else if (act.equalsIgnoreCase("pause"))
                    mPlayer.pause();
                else if (act.equalsIgnoreCase("stop"))
                    mPlayer.stop();
                else if (act.equalsIgnoreCase("duration"))
                    sendToActivity(getDuration(), "max");
                else if (act.equalsIgnoreCase("current"))
                    sendToActivity(getCurrentTime(), "curr");
            }
        }

        return Service.START_NOT_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {

        return null;
    }

    private void startVideo(final String vURL) {
        try {
            Log.d("MPLAY", "Entered MPLAY");

            PullURL attempt = new PullURL(vURL);
            attempt.startExtracting(new PullURL.YouTubeExtractorListener() {
                @Override
                public void onSuccess(PullURL.YouTubeExtractorResult result) {
                    final Uri res = result.getVideoUri();
                    Log.d("pull", res.toString());

                    Thread mThread = new Thread(new Runnable() {
                        public void run() {
                            try {
                                Log.d("MPLAY", "created thread");

                                mPlayer.setDataSource(BackgroundPlayer.this, res);
                                mPlayer.prepare();
                                mPlayer.start();

                                sendToActivity(getDuration(), "max");

                                Log.d("MPLAY", "Started");

                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });

                    mThread.start();

                    Log.d("MPLAY", "Thread Started");
                }

                @Override
                public void onFailure(Error error) {
                    Log.d("pull", "failed");
                    error.printStackTrace();
                }
            });


        }
        catch(Exception e) {
            e.printStackTrace();
        }
    }

    public String getDuration() {
        if(mPlayer.isPlaying())
            return Integer.toString(mPlayer.getDuration());
        else
            return null;
    }

    public String getCurrentTime() {
        if(mPlayer.isPlaying())
            return Integer.toString(mPlayer.getCurrentPosition());
        else
            return null;
    }


    public interface onTimeChange {
        void onChange(int time);
    }

    private void sendToActivity(String msg, String key) {
        Intent intent = new Intent("incoming");

        intent.putExtra(key, msg);
        LocalBroadcastManager.getInstance(getApplicationContext()).sendBroadcast(intent);
    }
}
