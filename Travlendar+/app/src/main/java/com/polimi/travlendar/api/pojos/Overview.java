package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

public class Overview {

    @SerializedName("bounds")
    @Expose
    private Bounds bounds;
    @SerializedName("cached")
    @Expose
    private Boolean cached;
    @SerializedName("calendar_id")
    @Expose
    private Integer calendarId;
    @SerializedName("departure")
    @Expose
    private Boolean departure;
    @SerializedName("distance")
    @Expose
    private Integer distance;
    @SerializedName("duration")
    @Expose
    private Integer duration;
    @SerializedName("end_address")
    @Expose
    private String endAddress;
    @SerializedName("end_date")
    @Expose
    private String endDate;
    @SerializedName("end_lat")
    @Expose
    private Double endLat;
    @SerializedName("end_lng")
    @Expose
    private Double endLng;
    @SerializedName("event_id")
    @Expose
    private Integer eventId;
    @SerializedName("flex_duration")
    @Expose
    private Object flexDuration;
    @SerializedName("id")
    @Expose
    private Integer id;
    @SerializedName("polyline")
    @Expose
    private String polyline;
    @SerializedName("reachable")
    @Expose
    private Boolean reachable;
    @SerializedName("start_address")
    @Expose
    private String startAddress;
    @SerializedName("start_date")
    @Expose
    private String startDate;
    @SerializedName("start_lat")
    @Expose
    private Double startLat;
    @SerializedName("start_lng")
    @Expose
    private Double startLng;
    @SerializedName("user_id")
    @Expose
    private Integer userId;

    public Bounds getBounds() {
        return bounds;
    }

    public void setBounds(Bounds bounds) {
        this.bounds = bounds;
    }

    public Boolean getCached() {
        return cached;
    }

    public void setCached(Boolean cached) {
        this.cached = cached;
    }

    public Integer getCalendarId() {
        return calendarId;
    }

    public void setCalendarId(Integer calendarId) {
        this.calendarId = calendarId;
    }

    public Boolean getDeparture() {
        return departure;
    }

    public void setDeparture(Boolean departure) {
        this.departure = departure;
    }

    public Integer getDistance() {
        return distance;
    }

    public void setDistance(Integer distance) {
        this.distance = distance;
    }

    public Integer getDuration() {
        return duration;
    }

    public void setDuration(Integer duration) {
        this.duration = duration;
    }

    public String getEndAddress() {
        return endAddress;
    }

    public void setEndAddress(String endAddress) {
        this.endAddress = endAddress;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public Double getEndLat() {
        return endLat;
    }

    public void setEndLat(Double endLat) {
        this.endLat = endLat;
    }

    public Double getEndLng() {
        return endLng;
    }

    public void setEndLng(Double endLng) {
        this.endLng = endLng;
    }

    public Integer getEventId() {
        return eventId;
    }

    public void setEventId(Integer eventId) {
        this.eventId = eventId;
    }

    public Object getFlexDuration() {
        return flexDuration;
    }

    public void setFlexDuration(Object flexDuration) {
        this.flexDuration = flexDuration;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getPolyline() {
        return polyline;
    }

    public void setPolyline(String polyline) {
        this.polyline = polyline;
    }

    public Boolean getReachable() {
        return reachable;
    }

    public void setReachable(Boolean reachable) {
        this.reachable = reachable;
    }

    public String getStartAddress() {
        return startAddress;
    }

    public void setStartAddress(String startAddress) {
        this.startAddress = startAddress;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public Double getStartLat() {
        return startLat;
    }

    public void setStartLat(Double startLat) {
        this.startLat = startLat;
    }

    public Double getStartLng() {
        return startLng;
    }

    public void setStartLng(Double startLng) {
        this.startLng = startLng;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

}