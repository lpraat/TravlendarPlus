package com.polimi.travlendar.api.pojos;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

public class Jwt{

    @SerializedName("id")
    @Expose
    private Integer id;
    @SerializedName("auth_token")
    @Expose
    private String authToken;

    public Jwt(Integer id, String authToken) {
        this.id = id;
        this.authToken = authToken;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getAuthToken() {
        return authToken;
    }

    public void setAuthToken(String authToken) {
        this.authToken = authToken;
    }

}
