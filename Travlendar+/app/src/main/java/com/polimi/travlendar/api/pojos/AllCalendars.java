package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;

public class AllCalendars {

    @SerializedName("calendars")
    @Expose
    private List<CalendarWithId> calendars = null;

    public List<CalendarWithId> getCalendars() {
        return calendars;
    }

    public void setCalendars(List<CalendarWithId> calendars) {
        this.calendars = calendars;
    }

}



