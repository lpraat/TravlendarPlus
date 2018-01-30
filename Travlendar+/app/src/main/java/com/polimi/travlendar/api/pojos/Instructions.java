package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;


public class Instructions {
    @SerializedName("overview")
    @Expose
    private Overview overview;
    @SerializedName("steps")
    @Expose
    private List<Step> steps = null;

    public Overview getOverview() {
        return overview;
    }

    public void setOverview(Overview overview) {
        this.overview = overview;
    }

    public List<Step> getSteps() {
        return steps;
    }

    public void setSteps(List<Step> steps) {
        this.steps = steps;
    }
}
