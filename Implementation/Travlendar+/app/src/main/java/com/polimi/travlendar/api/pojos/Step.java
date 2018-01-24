package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

public class Step {

    @SerializedName("arrival_stop")
    @Expose
    private Object arrivalStop;
    @SerializedName("arrival_time")
    @Expose
    private Object arrivalTime;
    @SerializedName("calendar_id")
    @Expose
    private Integer calendarId;
    @SerializedName("departure")
    @Expose
    private Boolean departure;
    @SerializedName("departure_stop")
    @Expose
    private Object departureStop;
    @SerializedName("departure_time")
    @Expose
    private Object departureTime;
    @SerializedName("distance")
    @Expose
    private Integer distance;
    @SerializedName("duration")
    @Expose
    private Integer duration;
    @SerializedName("end_lat")
    @Expose
    private Double endLat;
    @SerializedName("end_lng")
    @Expose
    private Double endLng;
    @SerializedName("event_id")
    @Expose
    private Integer eventId;
    @SerializedName("id")
    @Expose
    private Integer id;
    @SerializedName("instructions")
    @Expose
    private String instructions;
    @SerializedName("line_name")
    @Expose
    private Object lineName;
    @SerializedName("num_stops")
    @Expose
    private Object numStops;
    @SerializedName("overview_id")
    @Expose
    private Integer overviewId;
    @SerializedName("polyline")
    @Expose
    private String polyline;
    @SerializedName("start_lat")
    @Expose
    private Double startLat;
    @SerializedName("start_lng")
    @Expose
    private Double startLng;
    @SerializedName("transit_mode")
    @Expose
    private String transitMode;
    @SerializedName("travel_mode")
    @Expose
    private String travelMode;
    @SerializedName("type")
    @Expose
    private Object type;
    @SerializedName("user_id")
    @Expose
    private Integer userId;

    public Object getArrivalStop() {
        return arrivalStop;
    }

    public void setArrivalStop(Object arrivalStop) {
        this.arrivalStop = arrivalStop;
    }

    public Object getArrivalTime() {
        return arrivalTime;
    }

    public void setArrivalTime(Object arrivalTime) {
        this.arrivalTime = arrivalTime;
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

    public Object getDepartureStop() {
        return departureStop;
    }

    public void setDepartureStop(Object departureStop) {
        this.departureStop = departureStop;
    }

    public Object getDepartureTime() {
        return departureTime;
    }

    public void setDepartureTime(Object departureTime) {
        this.departureTime = departureTime;
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

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getInstructions() {
        return instructions;
    }

    public void setInstructions(String instructions) {
        this.instructions = instructions;
    }

    public Object getLineName() {
        return lineName;
    }

    public void setLineName(Object lineName) {
        this.lineName = lineName;
    }

    public Object getNumStops() {
        return numStops;
    }

    public void setNumStops(Object numStops) {
        this.numStops = numStops;
    }

    public Integer getOverviewId() {
        return overviewId;
    }

    public void setOverviewId(Integer overviewId) {
        this.overviewId = overviewId;
    }

    public String getPolyline() {
        return polyline;
    }

    public void setPolyline(String polyline) {
        this.polyline = polyline;
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

    public String getTransitMode() {
        return transitMode;
    }

    public void setTransitMode(String transitMode) {
        this.transitMode = transitMode;
    }

    public String getTravelMode() {
        return travelMode;
    }

    public void setTravelMode(String travelMode) {
        this.travelMode = travelMode;
    }

    public Object getType() {
        return type;
    }

    public void setType(Object type) {
        this.type = type;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }
}