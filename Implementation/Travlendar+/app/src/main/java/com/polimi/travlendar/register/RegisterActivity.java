package com.polimi.travlendar.register;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.Utils;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.User;
import com.polimi.travlendar.api.pojos.UserId;
import com.polimi.travlendar.checkers.AccountChecker;
import com.polimi.travlendar.login.LoginActivity;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class RegisterActivity extends AppCompatActivity {

    private static final String REGISTERED = "registered";

    private View registerProgressView;
    private EditText firstNameView;
    private EditText lastNameView;
    private EditText emailView;
    private EditText passwordView;
    private EditText confirmPasswordView;
    private TextView registerErrorView;
    private Button registerButtonView;
    private boolean onProgress = false;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        registerProgressView = findViewById(R.id.register_progress);
        registerProgressView.setVisibility(View.INVISIBLE);
        registerButtonView = (Button) findViewById(R.id.register_button);

        registerErrorView = (TextView) findViewById(R.id.register_error);
        registerErrorView.setVisibility(View.INVISIBLE);

        firstNameView = (EditText) findViewById(R.id.first_name);
        lastNameView = (EditText) findViewById(R.id.last_name);
        emailView = (EditText) findViewById(R.id.email);
        passwordView = (EditText) findViewById(R.id.password);
        confirmPasswordView = (EditText) findViewById(R.id.confirm_password);

        registerButtonView.setOnClickListener(view -> register());
    }

    private void register() {

        if (onProgress) {
            return;
        }

        onProgress = true;

        Utils.hideKeyboardOnSubmit(this);

        firstNameView.setError(null);
        lastNameView.setError(null);
        emailView.setError(null);
        passwordView.setError(null);
        confirmPasswordView.setError(null);
        registerProgressView.setVisibility(View.VISIBLE);

        String firstName = firstNameView.getText().toString();
        String lastName = lastNameView.getText().toString();
        String email = emailView.getText().toString();
        String password = passwordView.getText().toString();
        String confirmPassword = confirmPasswordView.getText().toString();

        boolean cancel = false;
        View focusView = null;

        if (TextUtils.isEmpty(confirmPassword)) {
            confirmPasswordView.setError(getString(R.string.empty_error));
            focusView = confirmPasswordView;
            cancel = true;
        } else if (!AccountChecker.doPasswordsMatch(password, confirmPassword)) {
            confirmPasswordView.setError(getString(R.string.password_match_error));
            focusView = confirmPasswordView;
            cancel = true;
        }

        if (TextUtils.isEmpty(password)) {
            passwordView.setError(getString(R.string.empty_error));
            focusView = passwordView;
            cancel = true;
        } else if (!AccountChecker.isValidPassword(password)) {
            passwordView.setError(getString(R.string.password_error));
            focusView = passwordView;
            cancel = true;
        }

        if (TextUtils.isEmpty(email)) {
            emailView.setError(getString(R.string.empty_error));
            focusView = emailView;
            cancel = true;
        } else if (!AccountChecker.isValidEmail(email)) {
            emailView.setError(getString(R.string.email_error));
            focusView = emailView;
            cancel = true;
        }


        if (TextUtils.isEmpty(lastName)) {
            lastNameView.setError(getString(R.string.empty_error));
            focusView = firstNameView;
            cancel = true;
        } else if(!AccountChecker.isValidName(lastName)) {
            lastNameView.setError(getString(R.string.name_error));
            focusView = firstNameView;
            cancel = true;
        }


        if (TextUtils.isEmpty(firstName)) {
            firstNameView.setError(getString(R.string.empty_error));
            focusView = firstNameView;
            cancel = true;
        } else if(!AccountChecker.isValidName(firstName)) {
            firstNameView.setError(getString(R.string.name_error));
            focusView = firstNameView;
            cancel = true;
        }


        if (cancel) {
            registerProgressView.setVisibility(View.GONE);
            focusView.requestFocus();
            onProgress = false;
        } else {
            registerUser(firstName, lastName, email, password);
        }
    }

    private void registerUser(String firstName, String lastName, String email, String password) {
        ApiCreator.getApiService(this).createUser(new User(firstName, lastName, email, password)).enqueue(new Callback<UserId>() {
            @Override
            public void onResponse(Call<UserId> call, Response<UserId> response) {
                registerProgressView.setVisibility(View.GONE);
                if (response.isSuccessful()) {
                    startLoginActivity();
                } else {
                    registerErrorView.setText(getString(R.string.register_error));
                    registerErrorView.setVisibility(View.VISIBLE);
                    onProgress = false;
                }
            }

            @Override
            public void onFailure(Call<UserId> call, Throwable t) {
                registerProgressView.setVisibility(View.GONE);
                registerErrorView.setText(getString(R.string.register_error_http));
                registerErrorView.setVisibility(View.VISIBLE);
                onProgress = false;
                ToastLauncher.showConnectionError(getApplicationContext());
            }
        });
    }

    private void startLoginActivity() {
        Intent intent = new Intent(this, LoginActivity.class);
        intent.putExtra(REGISTERED, "");
        startActivity(intent);
        finish();
    }

}
