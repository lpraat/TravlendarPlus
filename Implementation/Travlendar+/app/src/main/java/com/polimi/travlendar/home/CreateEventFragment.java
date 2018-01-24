package com.polimi.travlendar.home;


import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.text.TextUtils;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.TextView;

import com.github.florent37.singledateandtimepicker.dialog.SingleDateAndTimePickerDialog;
import com.google.android.gms.common.GooglePlayServicesNotAvailableException;
import com.google.android.gms.common.GooglePlayServicesRepairableException;
import com.google.android.gms.location.places.Place;
import com.google.android.gms.location.places.ui.PlacePicker;
import com.kunzisoft.switchdatetime.SwitchDateTimeDialogFragment;
import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.Utils;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.Event;
import com.polimi.travlendar.api.pojos.EventId;
import com.polimi.travlendar.data.SharedPreferencesManager;

import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.List;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import static android.app.Activity.RESULT_OK;

public class CreateEventFragment extends Fragment {

    private static final String NORMAL = "NORMAL";
    private static final String DAILY = "DAILY";
    private static final String WEEKLY = "WEEKLY";
    private static final String MONTHLY = "MONTHLY";
    private static final String YEARLY = "YEARLY";
    private static final int PLACE_PICKER_REQUEST = 1;
    private static final String OK = "ok";
    private static final String CANCEL = "cancel";
    public static final String START_TIME = "Start Time";
    public static final String DIALOG_START_TIME_TAG = "dialog_start_time";
    public static final String END_TIME = "End Time";
    public static final String DIALOG_END_TIME_TAG = "dialog_end_time";
    public static final String UNTIL_TIME = "Until Time";
    public static final String DIALOG_UNTIL_TIME_TAG = "dialog_until_time";
    public static final String SELECT_FLEX_HOURS_AND_MINUTE_DURATION = "Select flex hours and minute duration";
    public static final String CALENDAR_ID = "calendar_id";
    private static final String TAG = CreateEventFragment.class.getName();

    private SimpleDateFormat formatter = new SimpleDateFormat("HH:mm", Locale.getDefault());
    private DecimalFormat df = new DecimalFormat("#.####");
    private SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
    private View createEventProgressView;
    private Button createEventButtonView;
    private TextView eventLocation;
    private EditText eventNameView;
    private Button startTimeButtonView;
    private Button endTimeButtonView;
    private Button pickLocationButtonView;
    private Button recurrenceRuleButtonView;
    private Button untilButtonView;
    private TextView createEventErrorView;
    private Switch nextIsBaseView;
    private Switch flexView;
    private Button flexDurationButtonView;
    private AlertDialog recurrenceDialog;
    private TextView startTimeView;
    private TextView endTimeView;
    private TextView untilTimeView;
    private TextView rruleView;
    private TextView flexDurationView;
    private boolean locationPicked;
    private boolean timesPicked;
    private boolean recurrencePicked;
    private String rrule;
    private boolean onProgress;
    private Float latitude;
    private Float longitude;
    private String name;
    private Date startDate;
    private Date endDate;
    private Date flexDuration;
    private Date untilDate;
    private int userId;
    private int calendarId;


    public CreateEventFragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_create_event, container, false);
    }

    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userId = SharedPreferencesManager.getUserId(getContext());
        calendarId = getArguments().getInt(CALENDAR_ID);

        createEventProgressView = view.findViewById(R.id.create_event_progress);
        createEventProgressView.setVisibility(View.INVISIBLE);

        createEventErrorView = view.findViewById(R.id.create_event_error);
        createEventErrorView.setVisibility(View.INVISIBLE);
        createEventErrorView.setFocusable(true);
        createEventErrorView.setFocusableInTouchMode(true);

        createEventButtonView = view.findViewById(R.id.create_event_button);

        eventNameView = view.findViewById(R.id.event_name);

        startTimeButtonView = view.findViewById(R.id.pick_start_time);
        endTimeButtonView = view.findViewById(R.id.pick_end_time);

        startTimeView = view.findViewById(R.id.start_time_text);
        endTimeView = view.findViewById(R.id.end_time_text);

        untilTimeView = view.findViewById(R.id.until_time_text);

        pickLocationButtonView = view.findViewById(R.id.pick_location);

        nextIsBaseView = view.findViewById(R.id.next_is_base);

        recurrenceRuleButtonView = view.findViewById(R.id.recurrence_rule);
        untilButtonView = view.findViewById(R.id.until);
        untilButtonView.setEnabled(false);

        flexView = view.findViewById(R.id.flex);
        flexDurationButtonView = view.findViewById(R.id.flex_duration);
        flexDurationButtonView.setEnabled(false);
        flexDurationView = view.findViewById(R.id.flex_duration_text);

        eventLocation = view.findViewById(R.id.create_event_location);

        recurrenceDialog = createRecurrencePickerDialog();
        rruleView = view.findViewById(R.id.recurrence_rule_text);

        // set listeners
        startTimeButtonView.setOnClickListener(view1 -> launchStartTimePicker());
        endTimeButtonView.setOnClickListener(view1 -> launchEndTimePicker());

        pickLocationButtonView.setOnClickListener(view1 -> launchPlacePicker());

        recurrenceRuleButtonView.setOnClickListener(view1 -> recurrenceDialog.show());
        untilButtonView.setOnClickListener(view1->launchUntilDurationPicker());

        flexDurationButtonView.setOnClickListener(view1 -> launchFlexDurationPicker());
        // disables/enables the flex duration button according to the flex switch
        flexView.setOnCheckedChangeListener((compoundButton, status) -> {
            flexDurationButtonView.setEnabled(status);
            if (!status) {
                flexDuration = null;
            }
        } );

        startTimeButtonView.setOnClickListener(view1 -> launchStartTimePicker());
        createEventButtonView.setOnClickListener(view1 -> create());
    }


    /**
     * Adds in the layout a picker to let the user choose the start time of the event
     */
    private void launchStartTimePicker() {
        SwitchDateTimeDialogFragment dateTimeDialogFragment = SwitchDateTimeDialogFragment.newInstance(
                START_TIME,
                OK,
                CANCEL
        );
        Date today = new Date(); // generates today date
        Calendar cal = Calendar.getInstance();
        cal.setTime(today);
        int year = cal.get(Calendar.YEAR);
        int month = cal.get(Calendar.MONTH);
        int day = cal.get(Calendar.DAY_OF_MONTH);
        int hour = cal.get(Calendar.HOUR);
        int minute = cal.get(Calendar.MINUTE);
        dateTimeDialogFragment.setMinimumDateTime(new GregorianCalendar(year, month, day, hour, minute).getTime());
        dateTimeDialogFragment.setDefaultHourOfDay(hour);
        dateTimeDialogFragment.setDefaultMinute(minute);
        dateTimeDialogFragment.setDefaultDay(day);
        dateTimeDialogFragment.setDefaultMonth(month);
        dateTimeDialogFragment.setDefaultYear(year);
        dateTimeDialogFragment.set24HoursMode(true);
        dateTimeDialogFragment.setOnButtonClickListener(new SwitchDateTimeDialogFragment.OnButtonClickListener() {
            @Override
            public void onPositiveButtonClick(Date date) {
                if (Utils.getDifferenceInSeconds(today, date) < 0) { // time is not in the future
                    startTimeButtonView.setError(getString(R.string.pick_start_time_error));
                    startTimeButtonView.setFocusable(true);
                    startTimeButtonView.setFocusableInTouchMode(true);
                    startTimeButtonView.requestFocus();
                } else {
                    startTimeButtonView.setError(null);
                    Date d = Utils.removeSeconds(date);
                    startDate = d;
                    startTimeView.setText(getString(R.string.start_time_text) + sdf.format(startDate));
                }
            }
            @Override
            public void onNegativeButtonClick(Date date) {
                // do nothing
            }
        });

        dateTimeDialogFragment.show(getActivity().getSupportFragmentManager(), DIALOG_START_TIME_TAG);

    }

    /**
     * Adds in the layout a picker to let the user choose the end time of the event
     */
    private void launchEndTimePicker() {

        if (startDate == null) {
            startTimeButtonView.setError(getString(R.string.pick_time_error));
            startTimeButtonView.setFocusable(true);
            startTimeButtonView.setFocusableInTouchMode(true);
            startTimeButtonView.requestFocus();
        } else {

            SwitchDateTimeDialogFragment dateTimeDialogFragment = SwitchDateTimeDialogFragment.newInstance(
                    END_TIME,
                    OK,
                    CANCEL
            );
            Calendar cal = Calendar.getInstance();
            cal.setTime(startDate);
            int year = cal.get(Calendar.YEAR);
            int month = cal.get(Calendar.MONTH);
            int day = cal.get(Calendar.DAY_OF_MONTH);
            int hour = cal.get(Calendar.HOUR);
            int minute = cal.get(Calendar.MINUTE);
            dateTimeDialogFragment.set24HoursMode(true);
            dateTimeDialogFragment.setMinimumDateTime(new GregorianCalendar(year, month, day, hour, minute).getTime());
            dateTimeDialogFragment.setDefaultHourOfDay(hour);
            dateTimeDialogFragment.setDefaultMinute(minute);
            dateTimeDialogFragment.setDefaultDay(day);
            dateTimeDialogFragment.setDefaultMonth(month);
            dateTimeDialogFragment.setDefaultYear(year);
            dateTimeDialogFragment.setOnButtonClickListener(new SwitchDateTimeDialogFragment.OnButtonClickListener() {
                @Override
                public void onPositiveButtonClick(Date date) {
                    Date d = Utils.removeSeconds(date);
                    endDate = d;
                    timesPicked = true;
                    endTimeView.setText(getString(R.string.end_time_text)+ sdf.format(endDate));
                }

                @Override
                public void onNegativeButtonClick(Date date) {
                }
            });

            dateTimeDialogFragment.show(getActivity().getSupportFragmentManager(), DIALOG_END_TIME_TAG);
        }
    }


    /**
     * Checks if the data inserted is correct and modifies the layout accordingly
     */
    private void create() {
        if (onProgress) {
            return;
        }

        onProgress = true;

        Utils.hideKeyboardOnSubmit(getActivity());

        flexDurationButtonView.setError(null);
        untilButtonView.setError(null);
        recurrenceRuleButtonView.setError(null);
        pickLocationButtonView.setError(null);
        startTimeButtonView.setError(null);
        endTimeButtonView.setError(null);
        eventNameView.setError(null);

        createEventProgressView.setVisibility(View.VISIBLE);
        createEventProgressView.requestFocus();

        name = eventNameView.getText().toString();


        boolean cancel = false;
        View focusView = null;


        if (flexView.isChecked()) {
            if (flexDuration != null) {

                Calendar cal = Calendar.getInstance();
                cal.setTime(flexDuration);
                int seconds = Utils.getSeconds(cal.get(Calendar.HOUR), cal.get(Calendar.MINUTE));

                if (seconds >= Utils.getDifferenceInSeconds(startDate, endDate)) {
                    flexDurationButtonView.setError(getString(R.string.flex_duration_pick_error));
                    flexDurationButtonView.setFocusableInTouchMode(true);
                    flexDurationButtonView.setFocusable(true);
                    focusView = flexDurationButtonView;
                    cancel = true;
                }
            } else {
                flexDurationButtonView.setError(getString(R.string.flex_duration_error));
                flexDurationButtonView.setFocusableInTouchMode(true);
                flexDurationButtonView.setFocusable(true);
                focusView = flexDurationButtonView;
                cancel = true;
            }
        }

        if (recurrencePicked) {

            if (untilButtonView.isEnabled()) {

                if (untilDate != null) {
                    if (!Utils.areDatesOneAfterTheOther(endDate, untilDate)) {
                        untilButtonView.setError(getString(R.string.until_date_error));
                        untilButtonView.setFocusableInTouchMode(true);
                        untilButtonView.setFocusable(true);
                        focusView = untilButtonView;
                        cancel = true;
                    }
                } else {
                    untilButtonView.setError(getString(R.string.until_date_pick_error));
                    untilButtonView.setFocusableInTouchMode(true);
                    untilButtonView.setFocusable(true);
                    focusView = untilButtonView;
                    cancel = true;
                }
            }

        } else {
            recurrenceRuleButtonView.setError(getString(R.string.pick_recurrence_error));
            recurrenceRuleButtonView.setFocusableInTouchMode(true);
            recurrenceRuleButtonView.setFocusableInTouchMode(true);
            focusView = recurrenceRuleButtonView;
            cancel = true;
        }


        if (!locationPicked) {
            pickLocationButtonView.setError(getString(R.string.pick_location_error));
            pickLocationButtonView.setFocusable(true);
            pickLocationButtonView.setFocusableInTouchMode(true);
            focusView = pickLocationButtonView;
            cancel = true;
        }


        if (!timesPicked) {
            if (startDate == null) {
                startTimeButtonView.setError(getString(R.string.pick_times_error));
                startTimeButtonView.setFocusable(true);
                startTimeButtonView.setFocusableInTouchMode(true);
                focusView = startTimeButtonView;
            } else {
                endTimeButtonView.setError(getString(R.string.pick_times_error));
                endTimeButtonView.setFocusable(true);
                endTimeButtonView.setFocusableInTouchMode(true);
                focusView = endTimeButtonView;
            }
            cancel = true;
        } else {
            if (!Utils.areDatesOneAfterTheOther(startDate, endDate)) {
                endTimeButtonView.setError(getString(R.string.pick_times_order_error));
                endTimeButtonView.setFocusable(true);
                endTimeButtonView.setFocusableInTouchMode(true);
                focusView = endTimeButtonView;
                cancel = true;
            }
        }
        
        if (TextUtils.isEmpty(name)) {
            eventNameView.setError(getString(R.string.empty_error));
            focusView = eventNameView;
            cancel = true;
        }


        if (cancel) {
            createEventProgressView.setVisibility(View.INVISIBLE);
            focusView.requestFocus();
            onProgress = false;

        } else {
            createEvent();
        }

    }

    /**
     * Creates an event by doing an API call
     */
    private void createEvent() {
        String name = eventNameView.getText().toString();
        String startTime = dateToString(startDate);
        String endTime = dateToString(endDate);
        List<Float> location = new ArrayList<>();
        location.add(latitude);
        location.add(longitude);
        boolean nextIsBase = nextIsBaseView.isChecked();
        String recurrenceRule = rrule;

        String untilTime = null;
        if (!recurrenceRule.equals(NORMAL)) {
            untilTime = dateToString(untilDate);
        }

        boolean flex = flexView.isChecked();
        Float flexDuration = null;
        if (flex) {
            Calendar cal = Calendar.getInstance();
            cal.setTime(this.flexDuration);
            flexDuration = (float) Utils.getSeconds(cal.get(Calendar.HOUR), cal.get(Calendar.MINUTE));
        }

        Event event = new Event(name, location, startTime, endTime, recurrenceRule, nextIsBase, untilTime,
                                flex, flexDuration);

        ApiCreator.getApiService(getContext()).createEvent(event, userId, calendarId).enqueue(new Callback<EventId>() {
            @Override
            public void onResponse(Call<EventId> call, Response<EventId> response) {
                if (response.isSuccessful()) {
                    startHomeActivity();
                } else {
                    createEventProgressView.setVisibility(View.GONE);
                    createEventErrorView.setText(getString(R.string.create_event_error));
                    createEventErrorView.setVisibility(View.VISIBLE);
                    createEventErrorView.requestFocus();
                    onProgress = false;
                }
            }

            @Override
            public void onFailure(Call<EventId> call, Throwable t) {
                createEventProgressView.setVisibility(View.GONE);
                setConnectionError();
                ToastLauncher.showConnectionError(getContext());
            }
        });

    }


    public void startHomeActivity() {
        Intent intent = new Intent(getActivity(), HomeActivity.class);
        startActivity(intent);
    }

    public void setConnectionError() {
        createEventErrorView.setText(getString(R.string.connection_error));
        createEventErrorView.setVisibility(View.VISIBLE);
        onProgress=false;
    }


    /**
     * Adds in the layout a picker to let the user choose the until time of the event
     */
    private void launchUntilDurationPicker() {

        if (endDate == null) {
            endTimeButtonView.setError(getString(R.string.pick_time_error));
            endTimeButtonView.setFocusable(true);
            endTimeButtonView.setFocusableInTouchMode(true);
            endTimeButtonView.requestFocus();
        } else {

            SwitchDateTimeDialogFragment dateTimeDialogFragment = SwitchDateTimeDialogFragment.newInstance(
                    UNTIL_TIME,
                    OK,
                    CANCEL
            );
            Calendar cal = Calendar.getInstance();
            cal.setTime(endDate);
            int year = cal.get(Calendar.YEAR);
            int month = cal.get(Calendar.MONTH);
            int day = cal.get(Calendar.DAY_OF_MONTH);
            int hour = cal.get(Calendar.HOUR);
            int minute = cal.get(Calendar.MINUTE);
            dateTimeDialogFragment.set24HoursMode(true);
            dateTimeDialogFragment.setMinimumDateTime(new GregorianCalendar(year, month, day+1, hour, minute).getTime());
            dateTimeDialogFragment.setMaximumDateTime(new GregorianCalendar(year+2, month, day, hour, minute).getTime());
            dateTimeDialogFragment.setDefaultHourOfDay(hour);
            dateTimeDialogFragment.setDefaultMinute(minute);
            dateTimeDialogFragment.setDefaultDay(day+1);
            dateTimeDialogFragment.setDefaultMonth(month);
            dateTimeDialogFragment.setDefaultYear(year);
            dateTimeDialogFragment.setOnButtonClickListener(new SwitchDateTimeDialogFragment.OnButtonClickListener() {
                @Override
                public void onPositiveButtonClick(Date date) {
                    Date d = Utils.removeSeconds(date);
                    untilDate = d;
                    untilTimeView.setText(getString(R.string.until_time_text) + sdf.format(untilDate));
                }

                @Override
                public void onNegativeButtonClick(Date date) {
                }
            });

            dateTimeDialogFragment.show(getActivity().getSupportFragmentManager(), DIALOG_UNTIL_TIME_TAG);

        }
    }

    /**
     * Adds in the layout a picker to let the user choose the flex duration of the event
     */
    private void launchFlexDurationPicker() {

        if (endDate == null) {
            endTimeButtonView.setError(getString(R.string.pick_time_error));
            endTimeButtonView.setFocusable(true);
            endTimeButtonView.setFocusableInTouchMode(true);
            endTimeButtonView.requestFocus();
        } else {
            Calendar defaultTime = Calendar.getInstance();
            defaultTime.set(Calendar.HOUR, 12);
            defaultTime.set(Calendar.MINUTE, 30);
            new SingleDateAndTimePickerDialog.Builder(getContext())
                    .mustBeOnFuture()
                    .title(SELECT_FLEX_HOURS_AND_MINUTE_DURATION)
                    .backgroundColor(Color.WHITE)
                    .mainColor(Color.BLUE)
                    .defaultDate(defaultTime.getTime())
                    .displayDays(false)
                    .listener(date -> {
                        Calendar cal = Calendar.getInstance();
                        cal.setTime(date);
                        flexDuration = date;
                        flexDurationView.setText(getString(R.string.flex_duration) + formatter.format(date));
                    })
                    .display();
        }
    }


    /**
     * Creates a dialog to let the user choose a recurrence rule
     */
    public AlertDialog createRecurrencePickerDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        builder.setTitle(R.string.pick_color)
                .setItems(R.array.rrule, (dialog, which) -> {
                    switch(which) {
                        case 0:
                            rrule = NORMAL;
                            rruleView.setText(getString(R.string.recurrence_rule) + " " + NORMAL);
                            setRecurrencePicked(which);
                            break;
                        case 1:
                            rrule = DAILY;
                            rruleView.setText(getString(R.string.recurrence_rule) + " " + DAILY);
                            setRecurrencePicked(which);
                            break;
                        case 2:
                            rrule = WEEKLY;
                            rruleView.setText(getString(R.string.recurrence_rule) + " " + WEEKLY);
                            setRecurrencePicked(which);
                            break;
                        case 3:
                            rrule = MONTHLY;
                            rruleView.setText(getString(R.string.recurrence_rule) + " " + MONTHLY);
                            setRecurrencePicked(which);
                            break;
                        case 4:
                            rrule = YEARLY;
                            rruleView.setText(getString(R.string.recurrence_rule) + " " + YEARLY);
                            setRecurrencePicked(which);
                            break;
                        default:
                            return;

                    }
                });
        return builder.create();
    }

    /**
     * Set in the layout the recurrence picked
     * @param which the index number in the array of strings populating the recurrence picker dialog
     */
    private void setRecurrencePicked(int which) {
        recurrencePicked = true;
        if (which != 0) {
            untilButtonView.setEnabled(true);
        } else {
            untilButtonView.setEnabled(false);
            untilDate = null;
        }
    }

    /**
     * Launches the google place picker.
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

    private String dateToString(Date d) {
        return sdf.format(d);
    }

    /**
     * Handles the latitude longitude pair get from the google picker.
     */
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PLACE_PICKER_REQUEST) {
            if (resultCode == RESULT_OK) {
                Place place = PlacePicker.getPlace(getActivity(), data);
                if (!place.getAddress().toString().equals("")) {
                    locationPicked = true;
                    eventLocation.setText(place.getAddress());
                    latitude = Float.parseFloat(df.format(place.getLatLng().latitude).replace(",", "."));
                    longitude = Float.parseFloat(df.format(place.getLatLng().longitude).replace(",", "."));
                }
            }
        }
    }
}
