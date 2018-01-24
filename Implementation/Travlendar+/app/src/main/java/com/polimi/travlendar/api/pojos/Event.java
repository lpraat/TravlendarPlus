package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;
public class Event {

    @SerializedName("name")
    @Expose
    private String name;
    @SerializedName("location")
    @Expose
    private List<Float> location = null;
    @SerializedName("start_time")
    @Expose
    private String startTime;
    @SerializedName("end_time")
    @Expose
    private String endTime;
    @SerializedName("recurrence_rule")
    @Expose
    private String recurrenceRule;
    @SerializedName("next_is_base")
    @Expose
    private Boolean nextIsBase;
    @SerializedName("until")
    @Expose
    private String until;
    @SerializedName("flex")
    @Expose
    private Boolean flex;
    @SerializedName("flex_duration")
    @Expose
    private Float flexDuration;

    public Event(String name, List<Float> location, String startTime, String endTime, String recurrenceRule, Boolean nextIsBase, String until, Boolean flex, Float flexDuration) {
        this.name = name;
        this.location = location;
        this.startTime = startTime;
        this.endTime = endTime;
        this.recurrenceRule = recurrenceRule;
        this.nextIsBase = nextIsBase;
        this.until = until;
        this.flex = flex;
        this.flexDuration = flexDuration;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<Float> getLocation() {
        return location;
    }

    public void setLocation(List<Float> location) {
        this.location = location;
    }

    public String getStartTime() {
        return startTime;
    }

    public void setStartTime(String startTime) {
        this.startTime = startTime;
    }

    public String getEndTime() {
        return endTime;
    }

    public void setEndTime(String endTime) {
        this.endTime = endTime;
    }

    public String getRecurrenceRule() {
        return recurrenceRule;
    }

    public void setRecurrenceRule(String recurrenceRule) {
        this.recurrenceRule = recurrenceRule;
    }

    public Boolean getNextIsBase() {
        return nextIsBase;
    }

    public void setNextIsBase(Boolean nextIsBase) {
        this.nextIsBase = nextIsBase;
    }

    public String getUntil() {
        return until;
    }

    public void setUntil(String until) {
        this.until = until;
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
}
