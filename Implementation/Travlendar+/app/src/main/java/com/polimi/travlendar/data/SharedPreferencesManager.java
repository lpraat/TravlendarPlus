package com.polimi.travlendar.data;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.util.Log;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;


/**
 * This class provides methods to interface with the Android Preference Manager
 */
public class SharedPreferencesManager {

    // SharedPreferences keys
    private static final String TOKEN = "token";
    private static final String USER_ID = "userId";
    private static final String PASSWORD = "password";
    private static final String TAG = SharedPreferencesManager.class.getName();


    public static void addToken(Context context, String token) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putString(TOKEN, token);
        editor.apply();
    }

    public static void storeUserId(Context context, int id) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putInt(USER_ID, id);
        editor.apply();
    }

    public static void storePassword(Context context, String passwordHash) {
        SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putString(PASSWORD, hashPassword(passwordHash));
        editor.apply();
    }

    public static String hashPassword(String password) {
        try {
            // here it is not used an algorithm like bcrypt for performance issues on Android
            MessageDigest messageDigest = MessageDigest.getInstance("SHA-256");
            messageDigest.update(password.getBytes());
            return new String(messageDigest.digest());
        } catch (NoSuchAlgorithmException e) {
            Log.d(TAG, Log.getStackTraceString(e));
            return "";
        }
    }

    public static String getPassword(Context context) {
        return PreferenceManager.getDefaultSharedPreferences(context).getString(PASSWORD, "");
    }

    public static int getUserId(Context context) {
        return PreferenceManager.getDefaultSharedPreferences(context).getInt(USER_ID, 0);
    }

    public static void clearPreferences(Context context) {
        PreferenceManager.getDefaultSharedPreferences(context).edit().clear().apply();
    }
}
