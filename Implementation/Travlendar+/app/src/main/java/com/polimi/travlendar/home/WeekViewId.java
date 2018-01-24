package com.polimi.travlendar.home;

/**
 * This class is used by the ScheduleFragment class to store information
 * about recurrences in the user schedule.
 */
class WeekViewId {

    private int calendarId;
    private int eventId;
    private int recurrenceId;

    WeekViewId(int calendarId, int eventId, int recurrenceId) {
        this.calendarId = calendarId;
        this.eventId = eventId;
        this.recurrenceId = recurrenceId;
    }

    int getCalendarId() {
        return calendarId;
    }

    int getEventId() {
        return eventId;
    }

    int getRecurrenceId() {
        return recurrenceId;
    }
}
