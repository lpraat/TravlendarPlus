package com.polimi.travlendar.checkers;

import java.util.regex.Pattern;

/**
 * This class is used for checking user account data.
 */
public class AccountChecker {

    private static final Pattern EMAIL_PATTERN = Pattern.compile(
            "[a-zA-Z0-9\\+\\.\\_\\%\\-\\+]{1,256}" +
                    "\\@" +
                    "[a-zA-Z0-9][a-zA-Z0-9\\-]{0,64}" +
                    "(" +
                    "\\." +
                    "[a-zA-Z0-9][a-zA-Z0-9\\-]{0,25}" +
                    ")+"
    );

    private static final Pattern NAME_PATTERN = Pattern.compile(
            "^[a-zA-Z]+$"
    );

    private static final int passwordMinLength = 8;

    public static boolean isValidEmail(String email) {
        return EMAIL_PATTERN.matcher(email).matches();
    }

    public static boolean isValidPassword(String password) {
        return password.length() >= passwordMinLength;
    }

    public static boolean doPasswordsMatch(String password, String confirmPassword) {
        return password.equals(confirmPassword);

    }
    public static boolean isValidName(String name) {
        return NAME_PATTERN.matcher(name).matches();
    }
}
