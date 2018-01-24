package com.polimi.travlendar;

import com.polimi.travlendar.checkers.AccountChecker;

import org.junit.Test;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;


public class AccountCheckerTest {

    final private String VALID_EMAIL = "email1234@mail.it";
    final private String VALID_PASSWORD = "user13242";


    @Test
    public void isValidEmailTest() {
        assertTrue(AccountChecker.isValidEmail(VALID_EMAIL));
        assertFalse(AccountChecker.isValidEmail("user@gmail"));
        assertFalse(AccountChecker.isValidEmail("@user.it"));
    }

    @Test
    public void isValidPasswordTest() {
        assertFalse(AccountChecker.isValidPassword("test"));
        assertTrue(AccountChecker.isValidPassword(VALID_PASSWORD));
    }

    @Test
    public void doPasswordMatchTest() {
        assertFalse(AccountChecker.doPasswordsMatch(VALID_PASSWORD, "another_one"));
        assertTrue(AccountChecker.doPasswordsMatch(VALID_PASSWORD, VALID_PASSWORD));

    }

    @Test
    public void isValidNameTest() {
        assertFalse(AccountChecker.isValidName("Ab12"));
        assertTrue(AccountChecker.isValidName("Test"));
    }


}