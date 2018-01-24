package com.polimi.travlendar.login;

import android.content.Context;
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
import com.polimi.travlendar.api.RetrofitClient;
import com.polimi.travlendar.api.pojos.Jwt;
import com.polimi.travlendar.api.pojos.LoginUser;
import com.polimi.travlendar.checkers.AccountChecker;
import com.polimi.travlendar.data.SharedPreferencesManager;
import com.polimi.travlendar.home.HomeActivity;
import com.polimi.travlendar.register.RegisterActivity;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    private View loginProgressView;
    private EditText emailView;
    private EditText passwordView;
    private TextView registerTextView;
    private TextView loginErrorView;
    private Button loginButtonView;
    private static final String REGISTERED = "registered";
    private boolean onProgress = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        if (getIntent().hasExtra(REGISTERED)) {
            findViewById(R.id.register_success).setVisibility(View.VISIBLE);
        }

        loginProgressView = findViewById(R.id.login_progress);
        loginProgressView.setVisibility(View.INVISIBLE);

        loginErrorView = (TextView) findViewById(R.id.login_error);
        loginErrorView.setVisibility(View.INVISIBLE);

        emailView = (EditText) findViewById(R.id.email);
        passwordView = (EditText) findViewById(R.id.password);
        registerTextView = (TextView) findViewById(R.id.register_text);
        loginButtonView = (Button) findViewById(R.id.login_button);

        // set listeners
        registerTextView.setOnClickListener(view -> startRegisterActivity());
        loginButtonView.setOnClickListener(view -> login());
    }

    /**
     * Checks if the input data is correct and modifies the layout accordingly.
     */
    private void login() {

        if (onProgress) {
            return;
        }

        onProgress = true;

        // hide keyboard on login click
        Utils.hideKeyboardOnSubmit(this);

        emailView.setError(null);
        passwordView.setError(null);
        loginProgressView.setVisibility(View.VISIBLE);
        loginErrorView.setVisibility(View.INVISIBLE);

        String email = emailView.getText().toString();
        String password = passwordView.getText().toString();

        boolean cancel = false;
        View focusView = null;

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

        if (cancel) {
            loginProgressView.setVisibility(View.GONE);
            focusView.requestFocus();
            onProgress = false;
        } else {
            loginUser(email, password);
        }

    }

    @Override
    public void onBackPressed() {
        // do nothing
    }

    /**
     * Logs in the user by doing an API call.
     * After logging in the user it stores the Token sent by the API client side.
     */
    private void loginUser(String email, String password) {
        ApiCreator.getApiService(this).loginUser(new LoginUser(email, password)).enqueue(new Callback<Jwt>() {
            @Override
            public void onResponse(Call<Jwt> call, Response<Jwt> response) {

                loginProgressView.setVisibility(View.GONE);

                if (response.isSuccessful()) {
                    Jwt jwtResponse = response.body();
                    Context context = getApplicationContext();
                    SharedPreferencesManager.addToken(context, jwtResponse.getAuthToken());
                    SharedPreferencesManager.storePassword(context, password);
                    SharedPreferencesManager.storeUserId(context, jwtResponse.getId());
                    RetrofitClient.retrofit = null; // forcing retrofit to create a new client where
                                                    // the Authorization: Bearer header is added
                    startHomeActivity();
                } else {
                    loginErrorView.setText(getString(R.string.login_error));
                    loginErrorView.setVisibility(View.VISIBLE);
                    onProgress = false;
                }
            }


            @Override
            public void onFailure(Call<Jwt> call, Throwable t) {
                loginProgressView.setVisibility(View.GONE);
                loginErrorView.setText(R.string.login_error_http);
                loginErrorView.setVisibility(View.VISIBLE);
                onProgress = false;
                ToastLauncher.showConnectionError(getApplicationContext());
            }
        });

    }

    private void startRegisterActivity() {
        if (onProgress) {
            return;
        }
        Intent intent = new Intent(this, RegisterActivity.class);
        startActivity(intent);
    }

    private void startHomeActivity() {
        Intent intent = new Intent(this, HomeActivity.class);
        startActivity(intent);
        finish();
    }
}
