package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;

public class Preference {
    @SerializedName("name")
    @Expose
    private String name;
    @SerializedName("time")
    @Expose
    private List<String> time = null;
    @SerializedName("mileage")
    @Expose
    private Integer mileage;

    public Preference(String name, List<String> time, Integer mileage) {
        this.name = name;
        this.time = time;
        this.mileage = mileage;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<String> getTime() {
        return time;
    }

    public void setTime(List<String> time) {
        this.time = time;
    }

    public Integer getMileage() {
        return mileage;
    }

    public void setMileage(Integer mileage) {
        this.mileage = mileage;
    }
}