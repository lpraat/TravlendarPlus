package com.polimi.travlendar.api;


import android.content.Context;

public class ApiCreator {

    private static final String BASE_URL = "http://35.205.121.52:8000";

    /**
     * Returns a client that is able to do REST call to the Travlendar API
     */
    public static TravlendarApi getApiService(Context context) {
        RetrofitClient.retrofit = null;
        return RetrofitClient.getClient(context, BASE_URL).create(TravlendarApi.class);
    }
}

