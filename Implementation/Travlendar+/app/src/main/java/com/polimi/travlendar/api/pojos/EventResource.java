package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;

public class EventResource {
    @SerializedName("end_time")
    @Expose
    private String endTime;
    @SerializedName("flex")
    @Expose
    private Boolean flex;
    @SerializedName("flex_duration")
    @Expose
    private Float flexDuration;
    @SerializedName("location")
    @Expose
    private List<Float> location = null;
    @SerializedName("name")
    @Expose
    private String name;
    @SerializedName("next_is_base")
    @Expose
    private Boolean nextIsBase;
    @SerializedName("recurrence_rule")
    @Expose
    private String recurrenceRule;
    @SerializedName("recurrences")
    @Expose
    private List<EventRecurrence> recurrences = null;
    @SerializedName("start_time")
    @Expose
    private String startTime;
    @SerializedName("until")
    @Expose
    private String until;

    public String getEndTime() {
        return endTime;
    }

    public void setEndTime(String endTime) {
        this.endTime = endTime;
    }

    public Boolean getFlex() {
        return flex;
    }

    public void setFlex(Boolean flex) {
        this.flex = flex;
    }

    public Float getFlexDuration() {
        return flexDuration;
    }

    public void setFlexDuration(Float flexDuration) {
        this.flexDuration = flexDuration;
    }

    public List<Float> getLocation() {
        return location;
    }

    public void setLocation(List<Float> location) {
        this.location = location;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Boolean getNextIsBase() {
        return nextIsBase;
    }

    public void setNextIsBase(Boolean nextIsBase) {
        this.nextIsBase = nextIsBase;
    }

    public String getRecurrenceRule() {
        return recurrenceRule;
    }

    public void setRecurrenceRule(String recurrenceRule) {
        this.recurrenceRule = recurrenceRule;
    }

    public List<EventRecurrence> getRecurrences() {
        return recurrences;
    }

    public void setRecurrences(List<EventRecurrence> recurrences) {
        this.recurrences = recurrences;
    }

    public String getStartTime() {
        return startTime;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    public String getUntil() {
        return until;
    }

    public void setUntil(String until) {
        this.until = until;
    }
}
