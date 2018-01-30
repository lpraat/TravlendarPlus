package com.polimi.travlendar.api;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;

import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;


public class RetrofitClient {

    public static Retrofit retrofit = null;

    /**
     * Builds a retrofit client by adding proper headers and a response encoder/decoder(Gson)
     * @param baseUrl the baseUrl the client will be built for
     * @return a retrofit client
     */
    public static Retrofit getClient(Context context, String baseUrl) {

        if (retrofit==null) {

            Gson gson = new GsonBuilder()
                    .serializeNulls()
                    .create();

            SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);

            if (preferences.contains("token")) { // the user is logged in

                OkHttpClient client = new OkHttpClient.Builder().addInterceptor(new Interceptor() {
                    @Override
                    public Response intercept(Chain chain) throws IOException {
                        Request newRequest = chain.request().newBuilder()
                                .addHeader("Authorization", "Bearer " + preferences.getString("token", ""))
                                .addHeader("Content-Type", "application/json")
                                .build();
                        return chain.proceed(newRequest);
                    }
                }).build();


                retrofit = new Retrofit.Builder()
                        .client(client)
                        .baseUrl(baseUrl)
                        .addConverterFactory(GsonConverterFactory.create(gson))
                        .build();
            } else { // user is not logged in
                retrofit = new Retrofit.Builder()
                        .baseUrl(baseUrl)
                        .addConverterFactory(GsonConverterFactory.create(gson))
                        .build();
            }
        }
        return retrofit;
    }
}
