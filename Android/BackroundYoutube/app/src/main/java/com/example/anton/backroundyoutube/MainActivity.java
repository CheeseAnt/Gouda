package com.example.anton.backroundyoutube;

import android.app.AlertDialog;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.support.annotation.RequiresApi;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.NotificationCompat;
import android.support.v4.content.LocalBroadcastManager;
import android.text.InputType;
import android.util.Log;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.EditText;
import android.widget.RemoteViews;
import android.widget.SeekBar;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.Locale;

import static java.lang.Math.floor;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    @RequiresApi(api = Build.VERSION_CODES.KITKAT_WATCH)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        JSONMenuReader rader = new JSONMenuReader(this);

        ArrayList<String> thing = rader.getCategories();
        for(int i = 0; i < thing.size(); i++)
            System.out.println(thing.get(i));

        ArrayList<String> thinger = new ArrayList<>();
        thinger.add(thing.get(0));

        thing = rader.getSubCategories(thinger);
        for(int i = 0; i < thing.size(); i++)
            System.out.println(thing.get(i));

        thinger.add(thing.get(0));

        for(int i = 0; i < thinger.size(); i++)
            System.out.println(thinger.get(i));

        thing = rader.getSubCategories(thinger);
        for(int i = 0; i < thing.size(); i++)
            System.out.println(thing.get(i));

        thinger.add(thing.get(0));

        for(int i = 0; i < thinger.size(); i++)
            System.out.println(thinger.get(i));

        thing = rader.getDetail(thinger, "name");
        for(int i = 0; i < thing.size(); i++)
            System.out.println(thing.get(i));

        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        LocalBroadcastManager.getInstance(this).registerReceiver(mMessageReceiver, new IntentFilter("incoming"));

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                AlertDialog.Builder builder = new AlertDialog.Builder(MainActivity.this);
                builder.setTitle("Insert youtube URL");

                final EditText input = new EditText(MainActivity.this);
                input.setInputType(InputType.TYPE_CLASS_TEXT);
                builder.setView(input);

                builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String inputText = input.getText().toString();
                        System.out.println(inputText);

                        startBGPlay(inputText);

                        final Handler handler = new Handler();
                        handler.postDelayed(new Runnable() {
                            @Override
                            public void run() {


                            }
                        }, 7000);


                    }
                });
                builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                    }
                });

                builder.show();
            }
        });

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        System.out.println("Started");

        Intent now = new Intent(getBaseContext(), BackgroundPlayer.class);
        Bundle extras = getIntent().getExtras();
        if(extras != null) {
            String value = extras.getString(now.EXTRA_TEXT);

            System.out.println("found value: " + value);

            if(value != null) {
                String[] splits = value.split("/|=");

                System.out.println(splits[splits.length - 1]);

                now.putExtra("URL", splits[splits.length - 1]);
                getBaseContext().startService(now);

                makeNotificationControls();

                SeekBar sBar = (SeekBar) findViewById(R.id.seekBar);

                sBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                    @Override
                    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                        Log.d("onSeek", "Progress Changed");

                        if(fromUser) {
                            Intent duration = new Intent(MainActivity.this, BackgroundPlayer.class).putExtra("progress", progress);
                            getBaseContext().startService(duration);
                        }
                    }

                    @Override
                    public void onStartTrackingTouch(SeekBar seekBar) {

                        Log.d("onSeek", "onTrackStart");
                    }

                    @Override
                    public void onStopTrackingTouch(SeekBar seekBar) {

                        Log.d("onSeek", "onTrackStop");
                    }
                });

                final Handler handler = new Handler();
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        Intent duration = new Intent(MainActivity.this, BackgroundPlayer.class).setAction("current");
                        getBaseContext().startService(duration);
                        handler.postDelayed(this, 1000);
                    }
                }, 1000);
            }
        }

    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.nav_camera) {
            // Handle the camera action
        } else if (id == R.id.nav_gallery) {

        } else if (id == R.id.nav_slideshow) {

        } else if (id == R.id.nav_manage) {

        } else if (id == R.id.nav_share) {

        } else if (id == R.id.nav_send) {

        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    private BroadcastReceiver mMessageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String max = intent.getStringExtra("max");
            String curr = intent.getStringExtra("curr");
            int duration;

            SeekBar sBar = (SeekBar) findViewById(R.id.seekBar);

            if (max != null) {
                try {
                    duration = Integer.parseInt(max);
                    sBar.setMax(duration);
                    TextView timeDuration = (TextView) findViewById(R.id.totalTime);
                    double totalTime = ((double)duration/60000-floor((double)duration/60000))*60/100+floor((double)duration/60000);
                    timeDuration.setText(String.format(Locale.getDefault(), "%.2f", totalTime));
                    Log.d("Received", "Max set");
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
            }

            if (curr != null) {
                try {
                    duration = Integer.parseInt(curr);
                    sBar.setProgress(duration);

                    TextView timeCurrent = (TextView) findViewById(R.id.currentTime);
                    double currentTime = ((double)duration/60000-floor((double)duration/60000))*60/100+floor((double)duration/60000);
                    System.out.println(currentTime);
                    timeCurrent.setText(String.format(Locale.getDefault(), "%.2f", currentTime));


                    Log.d("Received", "Duration set");
                    Log.d("Received prog", Integer.toString(sBar.getProgress()));
                    Log.d("Received", curr);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    };

    private void startBGPlay(String inputText) {
        Intent now = new Intent(getBaseContext(), BackgroundPlayer.class);

        String[] splits = inputText.split("/|=");
        System.out.println(splits[splits.length - 1]);

        now.putExtra("URL", splits[splits.length-1]); // insert URL

        getBaseContext().startService(now);

    }

    private void makeNotificationControls() {
        Intent playIntent = new Intent(this, BackgroundPlayer.class).setAction("play");
        PendingIntent playbtn = PendingIntent.getService(this, 0, playIntent, 0);

        Intent pauseIntent = new Intent(this, BackgroundPlayer.class).setAction("pause");
        PendingIntent pausebtn = PendingIntent.getService(this, 0, pauseIntent, 0);

        Intent stopIntent = new Intent(this, BackgroundPlayer.class).setAction("stop");
        PendingIntent stopbtn = PendingIntent.getService(this, 0, stopIntent, 0);

        RemoteViews rViews = new RemoteViews(getPackageName(), R.layout.notification_layout);

        rViews.setImageViewResource(R.id.btnPlay, R.drawable.ic_play);
        rViews.setImageViewResource(R.id.btnPause, R.drawable.ic_pause);
        rViews.setImageViewResource(R.id.btnStop, R.drawable.ic_stop);

        rViews.setOnClickPendingIntent(R.id.btnPlay, playbtn);
        rViews.setOnClickPendingIntent(R.id.btnStop, stopbtn);
        rViews.setOnClickPendingIntent(R.id.btnPause, pausebtn);

        Notification builder = new NotificationCompat.Builder(this)
                .setContentTitle("Youtube Backgrounder")
                .setContentText("Pull Down for options")
                .setSmallIcon(R.drawable.play)
                .setStyle(new NotificationCompat.BigTextStyle().bigText("Play, Pause and Stop"))
                .setCustomBigContentView(rViews)
                .setShowWhen(true)
                .build();

        NotificationManager mnMan = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        mnMan.notify(1, builder);
    }
}
