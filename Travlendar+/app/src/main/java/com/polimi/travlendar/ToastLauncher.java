package com.polimi.travlendar;

import android.content.Context;
import android.widget.Toast;

/**
 * Util class for creating Android toasts.
 */
public class ToastLauncher {

    public static void showConnectionError(Context context) {
        Toast.makeText(context, R.string.connection_error, Toast.LENGTH_LONG).show();
    }

    public static void instructionsError(Context context) {
        Toast.makeText(context, R.string.instructions_error, Toast.LENGTH_LONG).show();
    }
}
