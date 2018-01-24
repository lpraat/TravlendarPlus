package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;

public class Calendar {


    @SerializedName("name")
    @Expose
    private String name;
    @SerializedName("description")
    @Expose
    private String description;
    @SerializedName("base")
    @Expose
    private List<Float> base = null;
    @SerializedName("color")
    @Expose
    private List<Integer> color = null;
    @SerializedName("active")
    @Expose
    private Boolean active;
    @SerializedName("carbon")
    @Expose
    private Boolean carbon;
    @SerializedName("preferences")
    @Expose
    private List<Preference> preferences = null;

    public Calendar(String name, String description, List<Float> base, List<Integer> color,
                    Boolean active, Boolean carbon, List<Preference> preferences) {
        this.name = name;
        this.description = description;
        this.base = base;
        this.color = color;
        this.active = active;
        this.carbon = carbon;
        this.preferences = preferences;
    }

    public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }

        public List<Float> getBase() {
            return base;
        }

        public void setBase(List<Float> base) {
            this.base = base;
        }

        public List<Integer> getColor() {
            return color;
        }

        public void setColor(List<Integer> color) {
            this.color = color;
        }

        public Boolean getActive() {
            return active;
        }

        public void setActive(Boolean active) {
            this.active = active;
        }

        public Boolean getCarbon() {
            return carbon;
        }

        public void setCarbon(Boolean carbon) {
            this.carbon = carbon;
        }

        public List<Preference> getPreferences() {
            return preferences;
        }

        public void setPreferences(List<Preference> preferences) {
            this.preferences = preferences;
        }


}


