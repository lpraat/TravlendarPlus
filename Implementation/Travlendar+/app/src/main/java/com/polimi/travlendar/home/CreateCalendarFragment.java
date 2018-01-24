package com.polimi.travlendar.home;


import android.app.AlertDialog;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.constraint.ConstraintLayout;
import android.support.constraint.ConstraintSet;
import android.support.v4.app.Fragment;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.NumberPicker;
import android.widget.Switch;
import android.widget.TextView;

import com.google.android.gms.common.GooglePlayServicesNotAvailableException;
import com.google.android.gms.common.GooglePlayServicesRepairableException;
import com.google.android.gms.location.places.Place;
import com.google.android.gms.location.places.ui.PlacePicker;
import com.pes.androidmaterialcolorpickerdialog.ColorPicker;
import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.Utils;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.CalendarId;
import com.polimi.travlendar.api.pojos.Preference;
import com.polimi.travlendar.api.pojos.Preferences;
import com.polimi.travlendar.data.SharedPreferencesManager;

import java.text.DecimalFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import static android.app.Activity.RESULT_OK;


public class CreateCalendarFragment extends Fragment {

    private static final int PLACE_PICKER_REQUEST = 1;
    private static final int MAXIMUM_MILEAGE = 1000;
    private static final int MINIMUM_MILEAGE = 0;
    private static final String SELECT_MILEAGE = "Select the maximum mileage";
    private static final String CHOOSE_VALUE = "Choose a value:";
    private static final String TAG = CreateEventFragment.class.getName();

    private ConstraintSet constraintSet = new ConstraintSet();
    private View createCalendarProgressView;
    private TextView createCalendarErrorView;
    private Button createCalendarButtonView;
    private EditText calendarNameView;
    private EditText calendarDescriptionView;
    private TextView latitudeView;
    private TextView longitudeView;
    private Button colorButtonView;
    private Button baseButtonView;
    private Switch activeSwitch;
    private Switch carbonSwitch;
    private ColorPicker cp;
    private DecimalFormat df = new DecimalFormat("#.####");
    private SimpleDateFormat format = new SimpleDateFormat("HH:mm", Locale.getDefault());
    private int colorRgb;
    private List<View> vehicleViews;
    private String name;
    private String description;
    private ConstraintLayout constraintLayout;
    private View fakeLayoutView;
    private boolean onProgress;
    private boolean positionPicked;
    private boolean colorPicked;
    private int userId;


    public CreateCalendarFragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_create_calendar, container, false);
    }

    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userId = SharedPreferencesManager.getUserId(getContext());

        constraintLayout = view.findViewById(R.id.create_calendar_layout);

        createCalendarProgressView = view.findViewById(R.id.create_calendar_progress);
        createCalendarProgressView.setVisibility(View.INVISIBLE);

        createCalendarErrorView = view.findViewById(R.id.create_calendar_error);
        createCalendarErrorView.setVisibility(View.INVISIBLE);
        createCalendarErrorView.setFocusable(true);
        createCalendarErrorView.setFocusableInTouchMode(true);

        createCalendarButtonView = view.findViewById(R.id.create_calendar_button);

        calendarNameView = view.findViewById(R.id.calendar_name);
        calendarDescriptionView = view.findViewById(R.id.calendar_description);

        colorButtonView = view.findViewById(R.id.color_button);

        baseButtonView = view.findViewById(R.id.base_button);

        activeSwitch = view.findViewById(R.id.active_switch);
        carbonSwitch = view.findViewById(R.id.carbon_switch);

        latitudeView = view.findViewById(R.id.latitude);
        longitudeView = view.findViewById(R.id.longitude);

        vehicleViews = new ArrayList<>();

        addFakePreference(); // for keeping the UI constraints in the layout

        // creates a new color picker and setup a listeners on it
        cp = new ColorPicker(getActivity());
        cp.setCallback(color -> {
            colorPicked = true;
            colorButtonView.setBackgroundColor(color);
            colorRgb = color;
            cp.dismiss();
        });

        onProgress = true;
        generateVehiclePreferences();


        // setup listeners
        baseButtonView.setOnClickListener(view1 -> launchPlacePicker());
        colorButtonView.setOnClickListener(view2 -> cp.show());
        createCalendarButtonView.setOnClickListener(v -> create());
    }


    /**
     * Checks the data inserted is correct and modifies the layout accordingly
     */
    private void create(){

        if (onProgress) {
            return;
        }

        onProgress = true;

        Utils.hideKeyboardOnSubmit(getActivity());

        calendarNameView.setError(null);
        colorButtonView.setError(null);
        baseButtonView.setError(null);

        for (int i = 0; i < vehicleViews.size(); i++) {
            Button startTimeButtonView = vehicleViews.get(i).findViewById(R.id.button_start_time);
            startTimeButtonView.setError(null);

            Button endTimeButtonView = vehicleViews.get(i).findViewById(R.id.button_end_time);
            endTimeButtonView.setError(null);
        }

        createCalendarProgressView.setVisibility(View.VISIBLE);
        createCalendarProgressView.requestFocus();

        name = calendarNameView.getText().toString();
        description = calendarDescriptionView.getText().toString();

        boolean cancel = false;
        View focusView = null;

        for (int i = vehicleViews.size()-1; i >= 0; i--) {
            View vehicleView = vehicleViews.get(i);

            Switch vehicleSwitch = vehicleView.findViewById(R.id.calendar_vehicle_switch);

            if (vehicleSwitch.isChecked()) {

                TextView startTimeView = vehicleView.findViewById(R.id.start_time);
                TextView endTimeView = vehicleView.findViewById(R.id.end_time);

                Button startTimeButtonView = vehicleView.findViewById(R.id.button_start_time);
                Button endTimeButtonView = vehicleView.findViewById(R.id.button_end_time);

                boolean startTimeChosen = !startTimeView.getText().equals(getString(R.string.start_time));
                boolean endTimeChosen = !endTimeView.getText().equals(getString(R.string.end_time));

                if (startTimeChosen && endTimeChosen) {
                    try {
                        Date startTime = format.parse(startTimeView.getText().toString());
                        Calendar calendar1 = Calendar.getInstance();
                        calendar1.setTime(startTime);
                        Date endTime = format.parse(endTimeView.getText().toString());
                        Calendar calendar2 = Calendar.getInstance();
                        calendar2.setTime(endTime);

                        if (!calendar2.getTime().after(calendar1.getTime())) {
                            startTimeButtonView.setFocusable(true);
                            startTimeButtonView.setFocusableInTouchMode(true);
                            startTimeButtonView.setError(getString(R.string.time_invalid_error));
                            endTimeButtonView.setError(getString(R.string.time_invalid_error));
                            focusView = startTimeButtonView;
                            cancel = true;
                        }

                    } catch (ParseException e) {
                        Log.d(TAG, Log.getStackTraceString(e));
                    }

                } else {

                    if (startTimeChosen) {
                        endTimeButtonView.setFocusable(true);
                        endTimeButtonView.setFocusableInTouchMode(true);
                        endTimeButtonView.setError(getString(R.string.pick_time_error));
                        focusView = endTimeButtonView;
                        cancel = true;
                    } else if (endTimeChosen) {
                        startTimeButtonView.setError(getString(R.string.pick_time_error));
                        startTimeButtonView.setFocusable(true);
                        startTimeButtonView.setFocusableInTouchMode(true);
                        focusView = startTimeButtonView;
                        cancel = true;
                    }
                }
            }
            // if it is not switched on do nothing
        }

        if (!colorPicked) {
            colorButtonView.setError(getString(R.string.color_error));
            colorButtonView.setFocusable(true);
            colorButtonView.setFocusableInTouchMode(true);
            focusView = colorButtonView;
            cancel = true;
        }

        if (!positionPicked) {
            baseButtonView.setError(getString(R.string.pick_location_error));
            baseButtonView.setFocusable(true);
            baseButtonView.setFocusableInTouchMode(true);
            focusView = baseButtonView;
            cancel = true;
        }

        if (TextUtils.isEmpty(name)) {
            calendarNameView.setError(getString(R.string.empty_error));
            focusView = calendarNameView;
            cancel = true;
        }

        if (cancel) {
            createCalendarProgressView.setVisibility(View.INVISIBLE);
            focusView.requestFocus();
            onProgress = false;

        } else {
            createCalendar();
        }
    }

    /**
     * Creates a calendar by doing an API call.
     */
    private void createCalendar() {

        List<Float> base = new ArrayList<>();
        base.add(Float.parseFloat(latitudeView.getText().toString().split(":")[1].replace(",", ".")));
        base.add(Float.parseFloat(longitudeView.getText().toString().split(":")[1].replace(",", ".")));

        List<Integer> color = new ArrayList<>();
        color.add(Color.red(colorRgb));
        color.add(Color.green(colorRgb));
        color.add(Color.blue(colorRgb));

        boolean active = activeSwitch.isChecked();
        boolean carbon = carbonSwitch.isChecked();

        List<Preference> preferences = new ArrayList<>();

        for (View vehicleView: vehicleViews) {

            Switch vehicleViewSwitch = vehicleView.findViewById(R.id.calendar_vehicle_switch);

            if (vehicleViewSwitch.isChecked()) {

                TextView startTimeView = vehicleView.findViewById(R.id.start_time);
                TextView endTimeView = vehicleView.findViewById(R.id.end_time);
                TextView mileageView = vehicleView.findViewById(R.id.mileage);

                List<String> times = null;
                if (!startTimeView.getText().equals(getString(R.string.start_time))) {
                    times = new ArrayList<>();
                    times.add(startTimeView.getText().toString());
                    times.add(endTimeView.getText().toString());
                }
                Integer mileage = null;
                if (!mileageView.getText().equals(getString(R.string.mileage))) {
                    mileage = Integer.parseInt(mileageView.getText().toString());

                    if (mileage == 0) {
                        mileage = null;
                    }
                }

                Switch vehicleSwitch = vehicleView.findViewById(R.id.calendar_vehicle_switch);
                String name = vehicleSwitch.getText().toString().toLowerCase();

                Preference preference = new Preference(name, times, mileage);
                preferences.add(preference);
            }
        }


        com.polimi.travlendar.api.pojos.Calendar calendar =
                new com.polimi.travlendar.api.pojos.Calendar(name, description, base, color, active, carbon, preferences);

        ApiCreator.getApiService(getActivity()).createCalendar(calendar, userId).enqueue(new Callback<CalendarId>() {
            @Override
            public void onResponse(Call<CalendarId> call, Response<CalendarId> response) {
                if (response.isSuccessful()) {
                    startHomeActivity();
                } else {
                    createCalendarProgressView.setVisibility(View.GONE);
                    createCalendarErrorView.setText(getString(R.string.create_calendar_error));
                    createCalendarErrorView.setVisibility(View.VISIBLE);
                    onProgress = false;
                }
            }

            @Override
            public void onFailure(Call<CalendarId> call, Throwable t) {
                createCalendarProgressView.setVisibility(View.GONE);
                createCalendarErrorView.setText(getText(R.string.create_calendar_error_http));
                createCalendarErrorView.setVisibility(View.VISIBLE);
                createCalendarErrorView.requestFocus();
                onProgress = false;
                ToastLauncher.showConnectionError(getContext());
            }
        });


    }

    /**
     * Updates the layout with a placeholder for keeping the constraints in the layout.
     */
    private void addFakePreference() {
        fakeLayoutView = getActivity().getLayoutInflater().inflate(R.layout.calendar_vehicle, constraintLayout, false);
        fakeLayoutView.setId(Utils.generateViewId());
        constraintLayout.addView(fakeLayoutView);

        constraintSet.clone(constraintLayout);
        constraintSet.connect(fakeLayoutView.getId(), ConstraintSet.TOP, colorButtonView.getId(), ConstraintSet.BOTTOM, 200);
        constraintSet.connect(createCalendarButtonView.getId(), ConstraintSet.TOP, fakeLayoutView.getId(), ConstraintSet.BOTTOM, 200);

        constraintSet.applyTo(constraintLayout);
    }


    /**
     * Gets user global preferences by doing an API call and substitutes the placeholder added
     * at view creation with the vehicle preference layouts
     */
    public void generateVehiclePreferences() {


        ApiCreator.getApiService(getActivity()).getPreferences(userId).enqueue(new Callback<Preferences>() {
            @Override
            public void onResponse(Call<Preferences> call, Response<Preferences> response) {
                if (response.isSuccessful()) {
                    constraintLayout.removeView(fakeLayoutView);

                    List<String> vehicles = response.body().getVehicles();

                    for (String s: vehicles) {
                        View vehicleView = getActivity().getLayoutInflater().inflate(R.layout.calendar_vehicle, constraintLayout, false);
                        vehicleView.setId(Utils.generateViewId());

                        Switch calendarVehicleSwitch = vehicleView.findViewById(R.id.calendar_vehicle_switch);
                        calendarVehicleSwitch.setChecked(true);

                        s = s.substring(0,1).toUpperCase() + s.substring(1).toLowerCase();
                        calendarVehicleSwitch.setText(s);


                        Button startTimeButtonView = vehicleView.findViewById(R.id.button_start_time);
                        Button endTimeButtonView = vehicleView.findViewById(R.id.button_end_time);
                        TextView startTimeView = vehicleView.findViewById(R.id.start_time);
                        TextView endTmeView = vehicleView.findViewById(R.id.end_time);

                        TimePickerDialog timePickerFragmentDialogStart = new TimePickerDialog(getContext(),
                                (timePicker, hour, minute) -> startTimeView.setText(Utils.getDateString(hour, Utils.roundMinute(minute))),
                                0, 0, true);
                        startTimeButtonView.setOnClickListener(view -> timePickerFragmentDialogStart.show());

                        TimePickerDialog timePickerFragmentDialogEnd = new TimePickerDialog(getContext(),
                                (timePicker, hour, minute) -> endTmeView.setText(Utils.getDateString(hour, Utils.roundMinute(minute))),
                                0, 0, true);
                        endTimeButtonView.setOnClickListener(view -> timePickerFragmentDialogEnd.show());


                        Button mileageButtonView = vehicleView.findViewById(R.id.mileage_button);
                        TextView mileageView = vehicleView.findViewById(R.id.mileage);
                        AlertDialog mileageDialog = createMileageDialog(mileageView);

                        mileageButtonView.setOnClickListener(view -> mileageDialog.show());

                        vehicleViews.add(vehicleView);
                        constraintLayout.addView(vehicleView);
                    }

                    constraintSet.clone(constraintLayout);
                    constraintSet.connect(vehicleViews.get(0).getId(), ConstraintSet.TOP, colorButtonView.getId(), ConstraintSet.BOTTOM, 200);
                    for (int i = 1; i < vehicleViews.size(); i++) {
                        constraintSet.connect(vehicleViews.get(i).getId(), ConstraintSet.TOP, vehicleViews.get(i-1).getId(), ConstraintSet.BOTTOM, 16);
                    }
                    constraintSet.connect(createCalendarButtonView.getId(), ConstraintSet.TOP, vehicleViews.get(vehicleViews.size()-1).getId(), ConstraintSet.BOTTOM, 200);
                    constraintSet.applyTo(constraintLayout);
                    onProgress = false;

                } else {
                    setConnectionError();
                    ToastLauncher.showConnectionError(getContext());
                }

            }

            @Override
            public void onFailure(Call<Preferences> call, Throwable t) {
                setConnectionError();
                ToastLauncher.showConnectionError(getContext());
            }
        });
    }


    /**
     * Creates a mileage dialog to show the user.
     * @param mileageView the textview to be updated after the user makes the choice
     */
    private AlertDialog createMileageDialog(TextView mileageView) {
        NumberPicker numberPicker = new NumberPicker(getActivity());
        numberPicker.setMaxValue(MAXIMUM_MILEAGE);
        numberPicker.setMinValue(MINIMUM_MILEAGE);

        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());

        builder.setView(numberPicker);
        builder.setTitle(SELECT_MILEAGE);
        builder.setMessage(CHOOSE_VALUE);

        builder
                .setPositiveButton(R.string.pick_mileage, (dialog, id) -> mileageView.setText(Integer.toString(numberPicker.getValue())))
                .setNegativeButton(R.string.cancel_pick, (dialog, id) -> dialog.cancel());
        return builder.create();
    }


    /**
     * Starts a new google place picker
     */
    public void launchPlacePicker() {
        PlacePicker.IntentBuilder builder = new PlacePicker.IntentBuilder();
        try {
            startActivityForResult(builder.build(getActivity()), PLACE_PICKER_REQUEST);
        } catch (GooglePlayServicesRepairableException e) {
            Log.e(TAG, Log.getStackTraceString(e));
        } catch (GooglePlayServicesNotAvailableException e) {
            Log.e(TAG, Log.getStackTraceString(e));
        }
    }

    /**
     * Handles the latitude longitude pair get in the google picker
     */
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PLACE_PICKER_REQUEST) {
            if (resultCode == RESULT_OK) {
                Place place = PlacePicker.getPlace(getActivity(), data);
                if (!place.getAddress().toString().equals("")) {
                    positionPicked = true;
                    latitudeView.setText(getString(R.string.latitude) + df.format(place.getLatLng().latitude));
                    longitudeView.setText(getString(R.string.longitude) + df.format(place.getLatLng().longitude));
                }
            }
        }
    }

    public void setConnectionError() {
        createCalendarProgressView.setVisibility(View.GONE);
        createCalendarErrorView.setText(getString(R.string.connection_error));
        createCalendarErrorView.setVisibility(View.VISIBLE);
        onProgress=false;
    }

    public void startHomeActivity() {
        Intent intent = new Intent(getActivity(), HomeActivity.class);
        startActivity(intent);
    }
}
