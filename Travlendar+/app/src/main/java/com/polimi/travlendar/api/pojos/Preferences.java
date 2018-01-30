package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;

public class Preferences {
    @SerializedName("personal_vehicles")
    @Expose
    private List<PersonalVehicle> personalVehicles = null;
    @SerializedName("vehicles")
    @Expose
    private List<String> vehicles = null;

    public Preferences(List<PersonalVehicle> personalVehicles, List<String> vehicles) {
        this.personalVehicles = personalVehicles;
        this.vehicles = vehicles;
    }

    public List<PersonalVehicle> getPersonalVehicles() {
        return personalVehicles;
    }

    public void setPersonalVehicles(List<PersonalVehicle> personalVehicles) {
        this.personalVehicles = personalVehicles;
    }

    public List<String> getVehicles() {
        return vehicles;
    }

    public void setVehicles(List<String> vehicles) {
        this.vehicles = vehicles;
    }
}