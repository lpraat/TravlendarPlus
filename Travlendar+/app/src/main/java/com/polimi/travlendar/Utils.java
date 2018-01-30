package com.polimi.travlendar;

import android.app.Activity;
import android.content.Context;
import android.view.inputmethod.InputMethodManager;

import java.util.Calendar;
import java.util.Date;
import java.util.concurrent.atomic.AtomicInteger;

public class Utils {

    private static final AtomicInteger sNextGeneratedId = new AtomicInteger(1);

    /**
     * Hides keyboard after a user clicks on a button.
     */
    public static void hideKeyboardOnSubmit(Activity activity) {
        InputMethodManager inputManager = (InputMethodManager)
                activity.getSystemService(Context.INPUT_METHOD_SERVICE);

        inputManager.hideSoftInputFromWindow((null == activity.getCurrentFocus()) ?
                null : activity.getCurrentFocus().getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);
    }

    /**
     * Generates a new ID for an element in a xml layout.
     */
    public static int generateViewId() {
        for (;;) {
            final int result = sNextGeneratedId.get();
            // aapt-generated IDs have the high byte nonzero; clamp to the range under that.
            int newValue = result + 1;
            if (newValue > 0x00FFFFFF) newValue = 1; // Roll over to 1, not 0.
            if (sNextGeneratedId.compareAndSet(result, newValue)) {
                return result;
            }
        }
    }

    /**
     * @param hour the hour
     * @param minute the minute
     * @return a string in the format HH:mm
     */
    public static String getDateString(int hour, int minute) {
        String h = String.valueOf(hour);
        if (h.length() == 1) {
            h = "0"+h;
        }
        String m = String.valueOf(minute);
        if (m.length() == 1) {
            m = "0"+m;
        }
        return h + ":" + m;
    }

    public static int roundMinute(int minute) {
        if (minute >= 30) {
            return 30;
        }
        return 0;
    }

    public static int getSeconds(int hour, int minute) {
        return hour*3600 + minute*60;
    }

    public static long getDifferenceInSeconds(Date d1, Date d2) {
        return (d2.getTime()-d1.getTime())/1000;
    }

    /**
     * Sets seconds to in a date.
     * @param d the date
     * @return the date with seconds set to 0
     */
    public static Date removeSeconds(Date d) {
        Calendar cal = Calendar.getInstance();
        cal.setTime(d);
        cal.set(Calendar.SECOND, 0);
        return cal.getTime();
    }

    /**
     * @return if d2 is in the future with respect to d1 false otherwise.
     */
    public static boolean areDatesOneAfterTheOther(Date d1, Date d2) {
        return Utils.getDifferenceInSeconds(d1, d2) > 0;
    }


}
