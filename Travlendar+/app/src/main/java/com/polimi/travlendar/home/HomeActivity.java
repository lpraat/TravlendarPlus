package com.polimi.travlendar.home;

import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.os.Handler;
import android.support.design.widget.NavigationView;
import android.support.v4.app.Fragment;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;

import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.AllCalendars;
import com.polimi.travlendar.api.pojos.CalendarWithId;
import com.polimi.travlendar.data.SharedPreferencesManager;
import com.polimi.travlendar.login.LoginActivity;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HomeActivity extends AppCompatActivity {

    public static final String CALENDAR_ID = "calendar_id";
    private ActionBarDrawerToggle actionBarDrawerToggle;
    private DrawerLayout drawerLayout;
    private NavigationView navigationView;
    private Menu menu;
    private List<Integer> calendarItemIds;

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getSupportActionBar().setDisplayShowTitleEnabled(false);
        setContentView(R.layout.activity_home);

        drawerLayout = (DrawerLayout) findViewById(R.id.drawer_layout);
        navigationView = (NavigationView) findViewById(R.id.navigation);

        calendarItemIds = new ArrayList<>();

        updateCalendarItems();
        setupDrawer();

        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setHomeButtonEnabled(true);

        if (savedInstanceState != null) {
            return;
        }

        // by default launch the schedule fragment
        ScheduleFragment scheduleFragment = new ScheduleFragment();
        getSupportFragmentManager().beginTransaction().add(R.id.fragment_container, scheduleFragment).commit();
    }

    /**
     * This function runs whenever the user presses on the back button of the phone
     */
    @Override
    public void onBackPressed() {
        Fragment currentFragment = getSupportFragmentManager().findFragmentById(R.id.fragment_container);
        if (!(currentFragment instanceof ScheduleFragment)) {
            getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, new ScheduleFragment()).addToBackStack(null).commit();
        }
        // else do nothing
    }

    /**
     * Gets the user calendar ids by doing an API call and updates the menu items in the
     * Navigation drawer accordingly.
     */
    private void updateCalendarItems() {
        menu = navigationView.getMenu();

        ApiCreator.getApiService(this).getAllCalendars(SharedPreferencesManager.getUserId(this)).enqueue(new Callback<AllCalendars>() {
            @Override
            public void onResponse(Call<AllCalendars> call, Response<AllCalendars> response) {

                List<CalendarWithId> calendarWithIdList = response.body().getCalendars();
                if (calendarWithIdList != null) {

                    if (response.isSuccessful()) {

                        for (CalendarWithId calendarWithId : calendarWithIdList) {
                            Integer newId = calendarWithId.getId();
                            calendarItemIds.add(newId);
                            menu.add(R.id.calendars, newId, 1, calendarWithId.getName());
                            MenuItem item = menu.findItem(newId);
                            item.setIcon(R.drawable.ic_action_name);
                            int r = calendarWithId.getColor().get(0);
                            int g = calendarWithId.getColor().get(1);
                            int b = calendarWithId.getColor().get(2);

                            Drawable drawable = item.getIcon();
                            if (drawable != null) {
                                // re color the icon of the calendar with the calendar color
                                drawable.mutate();
                                drawable.setColorFilter(Color.rgb(r, g, b), PorterDuff.Mode.SRC_ATOP);
                            }
                            item.setIcon(drawable);
                        }
                        invalidateOptionsMenu();

                    }
                }
            }

            @Override
            public void onFailure(Call<AllCalendars> call, Throwable t) {
                ToastLauncher.showConnectionError(getApplicationContext());
            }
        });
    }

    /**
     * Initializes actionBarDrawerToggle
     */
    public void setupDrawer() {
        actionBarDrawerToggle = new ActionBarDrawerToggle(this, drawerLayout,
                R.string.drawer_open, R.string.drawer_close) {

            /**
             * Called when a drawer has settled in a completely open state
             */
            @Override
            public void onDrawerOpened(View drawerView) {
                super.onDrawerOpened(drawerView);
                invalidateOptionsMenu(); // menu should be re-drawn
            }

            /**
             * Called when a drawer has settled in a completely closed state
             */
            @Override
            public void onDrawerClosed(View view) {
                super.onDrawerClosed(view);
                invalidateOptionsMenu();
            }
        };
        actionBarDrawerToggle.setDrawerIndicatorEnabled(true);
        drawerLayout.addDrawerListener(actionBarDrawerToggle);

        // set a listener for handling menu item clicked on the navigation view
        navigationView.setNavigationItemSelectedListener(item -> {
            Fragment currentFragment = getSupportFragmentManager().findFragmentById(R.id.fragment_container);
            int id = item.getItemId();
            switch (id) {

                case R.id.create_calendar:
                    if (!(currentFragment instanceof CreateCalendarFragment)) {
                        getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, new CreateCalendarFragment()).commit();
                    }
                    closeDrawer();
                    return true;

                case R.id.schedule:
                    if (!(currentFragment instanceof ScheduleFragment)) {
                        getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, new ScheduleFragment()).commit();
                    }
                    closeDrawer();
                    return true;

                case R.id.preferences:
                    if (!(currentFragment instanceof PreferencesFragment)) {
                        getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, new PreferencesFragment()).commit();
                    }
                    closeDrawer();
                    return true;

                case R.id.settings:
                    if (!(currentFragment instanceof AccountSettingsFragment)) {
                        getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, new AccountSettingsFragment()).commit();
                    }
                    closeDrawer();
                    return true;

                case R.id.logout:
                    logout();
                    return true;

                default:
                    // else the click is on a calendar item

                    for (Integer i: calendarItemIds) {
                        if (i == id) {
                            Bundle bundle = new Bundle();
                            bundle.putInt(CALENDAR_ID, i);
                            Fragment modifyCalendarFragment = new ModifyCalendarFragment();
                            modifyCalendarFragment.setArguments(bundle);
                            getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, modifyCalendarFragment).commit();
                            closeDrawer();
                            return true;
                        }
                    }
                    return true;
            }
        });
    }


    // to avoid lags
    private void closeDrawer() {
        new Handler().postDelayed(() -> drawerLayout.closeDrawers(), 200);
    }

    /**
     * Logout the user by deleting the token.
     */
    private void logout() {
        SharedPreferencesManager.clearPreferences(this);
        Intent intent = new Intent(this, LoginActivity.class);
        startActivity(intent);
        finish();
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Activate the navigation drawer toggle
        if (actionBarDrawerToggle.onOptionsItemSelected(item)) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onPostCreate(Bundle savedInstanceState) {
        super.onPostCreate(savedInstanceState);
        actionBarDrawerToggle.syncState();
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        actionBarDrawerToggle.onConfigurationChanged(newConfig);
    }

}
