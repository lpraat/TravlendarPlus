package com.polimi.travlendar.api.pojos;


import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

public class CalendarId {
    @SerializedName("user_id")
    @Expose
    private Integer userId;
    @SerializedName("id")
    @Expose
    private Integer id;

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }
}
