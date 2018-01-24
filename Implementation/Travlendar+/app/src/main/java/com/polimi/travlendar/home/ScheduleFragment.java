package com.polimi.travlendar.home;

import android.app.AlertDialog;
import android.graphics.Color;
import android.graphics.RectF;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.Fragment;
import android.text.format.DateFormat;
import android.util.Log;
import android.util.LongSparseArray;
import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;

import com.alamkanak.weekview.DateTimeInterpreter;
import com.alamkanak.weekview.MonthLoader;
import com.alamkanak.weekview.WeekView;
import com.alamkanak.weekview.WeekViewEvent;
import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.AllCalendars;
import com.polimi.travlendar.api.pojos.CalendarWithId;
import com.polimi.travlendar.api.pojos.Recurrence;
import com.polimi.travlendar.api.pojos.Recurrences;
import com.polimi.travlendar.data.SharedPreferencesManager;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ScheduleFragment extends Fragment implements WeekView.EventClickListener, MonthLoader.MonthChangeListener {

    public static final String CALENDAR_ID = "calendar_id";
    public static final String EVENT_ID = "event_id";
    public static final String RECURRENCE_ID = "recurrence_id";
    public static final String TAG = ScheduleFragment.class.getName();
    private WeekView mWeekView;
    private FloatingActionButton floatingActionButton;
    private SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
    private List<WeekViewEvent> events;
    private LongSparseArray<WeekViewId> eventsMap;
    private List<CalendarWithId> calendars;
    private boolean calledNetwork;
    private static final int TYPE_DAY_VIEW = 1;
    private static final int TYPE_THREE_DAY_VIEW = 2;
    private static final int TYPE_WEEK_VIEW = 3;
    private int mWeekViewType = TYPE_THREE_DAY_VIEW;
    private int userId;

    public ScheduleFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setHasOptionsMenu(true);
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_schedule, container, false);
    }

    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        userId = SharedPreferencesManager.getUserId(getContext());

        calledNetwork = false;
        events = new ArrayList<>();
        eventsMap = new LongSparseArray<>();

        // create the floating create event button and add a listener on it
        floatingActionButton = view.findViewById(R.id.floatingActionButton);
        floatingActionButton.setOnClickListener(view1 -> createCalendarPicker().show());

        // setup the schedule layout
        mWeekView = view.findViewById(R.id.weekView);
        mWeekView.setOnEventClickListener(this);
        mWeekView.setMonthChangeListener(this);

        setupDateTimeInterpreter(false);

    }

    /**
     * Defines how the date is displayed according to the view chosen by the user
     * For example if a week view is selected (less space for displaying the date)
     * the date is displayed in a more readable way.
     * @param shortDate boolean indicating whether the date should be short
     */
    private void setupDateTimeInterpreter(final boolean shortDate) {
        mWeekView.setDateTimeInterpreter(new DateTimeInterpreter() {
            @Override
            public String interpretDate(Calendar date) {
                SimpleDateFormat weekdayNameFormat = new SimpleDateFormat("EEE", Locale.getDefault());
                String weekday = weekdayNameFormat.format(date.getTime());
                SimpleDateFormat format;

                if (shortDate) {
                    format = new SimpleDateFormat(" M/d", Locale.getDefault());
                } else {
                    format = new SimpleDateFormat(" M/d/yy", Locale.getDefault());
                }
                // All android api level do not have a standard way of getting the first letter of
                // the week day name. Hence we get the first char programmatically.
                // Details: http://stackoverflow.com/questions/16959502/get-one-letter-abbreviation-of-week-day-of-a-date-in-java#answer-16959657
                if (shortDate)
                    weekday = String.valueOf(weekday.charAt(0));
                return weekday.toUpperCase() + format.format(date.getTime());
            }

            @Override
            public String interpretTime(int hour) {
                Calendar calendar = Calendar.getInstance();
                calendar.set(Calendar.HOUR_OF_DAY, hour);
                calendar.set(Calendar.MINUTE, 0);

                try {
                    SimpleDateFormat sdf = DateFormat.is24HourFormat(getContext()) ? new SimpleDateFormat("HH:mm", Locale.getDefault()) :
                                                                                     new SimpleDateFormat("hh a", Locale.getDefault());
                    return sdf.format(calendar.getTime());
                } catch (Exception e) {
                    Log.e(TAG, Log.getStackTraceString(e));
                    return "";
                }
            }
        });
    }


    /**
     * Change the mode in which the schedule is displayed according to user clicks in the menu items.
     * @param item the index of the item clicked, this index is declared in the xml layout file.
     */
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        setupDateTimeInterpreter(id == R.id.action_week_view);
        switch (id){
            case R.id.action_today:
                mWeekView.goToToday();
                return true;
            case R.id.action_day_view:
                if (mWeekViewType != TYPE_DAY_VIEW) {
                    item.setChecked(!item.isChecked());
                    mWeekViewType = TYPE_DAY_VIEW;
                    mWeekView.setNumberOfVisibleDays(1);

                    mWeekView.setColumnGap((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 8, getResources().getDisplayMetrics()));
                    mWeekView.setTextSize((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 12, getResources().getDisplayMetrics()));
                    mWeekView.setEventTextSize((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 12, getResources().getDisplayMetrics()));
                }
                return true;
            case R.id.action_three_day_view:
                if (mWeekViewType != TYPE_THREE_DAY_VIEW) {
                    item.setChecked(!item.isChecked());
                    mWeekViewType = TYPE_THREE_DAY_VIEW;
                    mWeekView.setNumberOfVisibleDays(3);

                    mWeekView.setColumnGap((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 8, getResources().getDisplayMetrics()));
                    mWeekView.setTextSize((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 12, getResources().getDisplayMetrics()));
                    mWeekView.setEventTextSize((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 12, getResources().getDisplayMetrics()));
                }
                return true;
            case R.id.action_week_view:
                if (mWeekViewType != TYPE_WEEK_VIEW) {
                    item.setChecked(!item.isChecked());
                    mWeekViewType = TYPE_WEEK_VIEW;
                    mWeekView.setNumberOfVisibleDays(7);

                    mWeekView.setColumnGap((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 2, getResources().getDisplayMetrics()));
                    mWeekView.setTextSize((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 10, getResources().getDisplayMetrics()));
                    mWeekView.setEventTextSize((int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, 10, getResources().getDisplayMetrics()));
                }
                return true;
        }

        return super.onOptionsItemSelected(item);
    }

    /**
     * Creates a calendar picker to let the user choose
     * on which calendar an event should be added.
     */
    private AlertDialog createCalendarPicker() {
        List<String> calendarNames = new ArrayList<>();
        for (CalendarWithId calendar: calendars) {
            calendarNames.add(calendar.getName());
        }
        CharSequence[] items = calendarNames.toArray(new String[calendarNames.size()]);
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        builder.setTitle(items.length != 0 ? R.string.pick_calendar : R.string.create_calendar_before_pick)
                .setItems(items, (dialog, which) -> {
                    Bundle bundle = new Bundle();
                    bundle.putInt(CALENDAR_ID, calendars.get(which).getId());
                    Fragment createEventFragment = new CreateEventFragment();
                    createEventFragment.setArguments(bundle);
                    getFragmentManager().beginTransaction().replace(R.id.fragment_container, createEventFragment).commit();
                });
        return builder.create();
    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
        inflater.inflate(R.menu.schedule_main, menu);
        super.onCreateOptionsMenu(menu, inflater);
    }

    /**
     * Handles the user touch on an event and displays a dialog the user can use
     * to access either to modify the event or to see the instructions for the event.
     * @param event the event cliked.
     */
    @Override
    public void onEventClick(WeekViewEvent event, RectF eventRect) {
        WeekViewId weekViewId = eventsMap.get(event.getId());
        Bundle bundle = new Bundle();
        bundle.putInt(CALENDAR_ID, weekViewId.getCalendarId());
        bundle.putInt(EVENT_ID, weekViewId.getEventId());
        bundle.putInt(RECURRENCE_ID, weekViewId.getRecurrenceId());

        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        builder.setMessage(R.string.ask_event)
                .setPositiveButton(R.string.ask_modify_event, (dialog, id) -> {
                    Fragment modifyEventFragment = new ModifyEventFragment();
                    modifyEventFragment.setArguments(bundle);
                    getFragmentManager().beginTransaction().replace(R.id.fragment_container, modifyEventFragment).commit();
                })
                .setNegativeButton(R.string.ask_instruction_event, (dialog, id) -> {
                    Fragment travelInstructionsFragment = new TravelInstructionsFragment();
                    travelInstructionsFragment.setArguments(bundle);
                    getFragmentManager().beginTransaction().replace(R.id.fragment_container, travelInstructionsFragment).commit();
                });

        AlertDialog dialog = builder.create();
        dialog.setCanceledOnTouchOutside(true);
        dialog.show();
    }

    /**
     * Find the calendar color for a calendar
     * @param calendarId the id of the calendar to find the color for.
     * @param calendarWithIds the list of calendar ids to check.
     */
    private int findCalendarColor(int calendarId, List<CalendarWithId> calendarWithIds) {

        for (CalendarWithId calendarWithId : calendarWithIds) {
            if (calendarWithId.getId().equals(calendarId)) {
                List<Integer> color = calendarWithId.getColor();
                return Color.rgb(color.get(0), color.get(1), color.get(2));
            }
        }
        return 0;
    }


    /**
     * Checks if an event falls into a specific year and month.
     * @param event The event to check for.
     * @param year The year.
     * @param month The month.
     * @return True if the event matches the year and month.
     */
    private boolean eventMatches(WeekViewEvent event, int year, int month) {
        return (event.getStartTime().get(Calendar.YEAR) == year && event.getStartTime().get(Calendar.MONTH) == month - 1) || (event.getEndTime().get(Calendar.YEAR) == year && event.getEndTime().get(Calendar.MONTH) == month - 1);
    }


    /**
     * Does an API call to get all the user events and build up the user schedule.
     * After getting the schedule the WeekViewEvent list is populated and ready to be consumed
     * by the onMonthChange listener.
     */
    private void populateEvents() {

        ApiCreator.getApiService(getContext()).getAllCalendars(userId).enqueue(new Callback<AllCalendars>() {
            @Override
            public void onResponse(Call<AllCalendars> call, Response<AllCalendars> response) {
                if (response.isSuccessful()) {

                    calendars = response.body().getCalendars();
                    ApiCreator.getApiService(getContext()).getSchedule(userId).enqueue(new Callback<Recurrences>() {
                        @Override
                        public void onResponse(Call<Recurrences> call, Response<Recurrences> response) {
                            if (response.isSuccessful()) {

                                List<Recurrence> recurrences = response.body().getRecurrences();

                                for (Recurrence recurrence : recurrences) {
                                    String startTimeStr = recurrence.getStartTime();
                                    String endTimeStr = recurrence.getEndTime();
                                    String eventName = recurrence.getEventName();

                                    try {
                                        Calendar startCal = Calendar.getInstance();
                                        startCal.setTime(sdf.parse(startTimeStr));
                                        Calendar endCal = Calendar.getInstance();
                                        endCal.setTime(sdf.parse(endTimeStr));
                                        WeekViewEvent event = new WeekViewEvent(recurrences.indexOf(recurrence), eventName, startCal, endCal);
                                        event.setColor(findCalendarColor(recurrence.getCalendarId(), calendars));
                                        events.add(event);
                                        eventsMap.put(event.getId(), new WeekViewId(recurrence.getCalendarId(), recurrence.getEventId(), recurrence.getId()));
                                    } catch (ParseException e) {
                                        Log.e(TAG, Log.getStackTraceString(e));
                                    }
                                }
                                mWeekView.notifyDatasetChanged();
                            }
                        }
                        @Override
                        public void onFailure(Call<Recurrences> call, Throwable t) {
                            ToastLauncher.showConnectionError(getContext());
                        }
                    });
                }
            }

            @Override
            public void onFailure(Call<AllCalendars> call, Throwable t) {
                ToastLauncher.showConnectionError(getContext());
            }
        });
    }

    /**
     * The layout showing the schedule loads by default 3 months, the current one(the one the user
     * is viewing) the past one and the future one. This listener takes the events by the WeekViewEvent lists
     * populated by populateEvents function and it is called 3 times for each month loaded.
     */
    @Override
    public List<? extends WeekViewEvent> onMonthChange(int newYear, int newMonth) {
        if (!calledNetwork) {
            populateEvents();
            calledNetwork = true;
        }

        List<WeekViewEvent> matchedEvents = new ArrayList<>();
        for (WeekViewEvent event : events) {
            if (eventMatches(event, newYear, newMonth)) {
                matchedEvents.add(event);
            }
        }
        return matchedEvents;
    }
}
