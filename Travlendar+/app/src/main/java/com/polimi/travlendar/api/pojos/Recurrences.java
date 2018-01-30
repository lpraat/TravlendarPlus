package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;


public class Recurrences {
    @SerializedName("recurrences")
    @Expose
    private List<Recurrence> recurrences = null;

    public List<Recurrence> getRecurrences() {
        return recurrences;
    }

    public void setRecurrences(List<Recurrence> recurrences) {
        this.recurrences = recurrences;
    }
}
