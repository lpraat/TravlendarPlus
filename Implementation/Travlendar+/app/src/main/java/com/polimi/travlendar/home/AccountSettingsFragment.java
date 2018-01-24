package com.polimi.travlendar.home;


import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.Utils;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.User;
import com.polimi.travlendar.api.pojos.UserId;
import com.polimi.travlendar.api.pojos.UserResource;
import com.polimi.travlendar.checkers.AccountChecker;
import com.polimi.travlendar.data.SharedPreferencesManager;
import com.polimi.travlendar.login.LoginActivity;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class AccountSettingsFragment extends Fragment {

    private String currentFirstName;
    private String currentLastName;
    private String currentEmail;
    private EditText firstNameView;
    private EditText lastNameView;
    private EditText emailView;
    private EditText newPasswordView;
    private EditText confirmNewPasswordView;
    private EditText currentPasswordView;
    private Button updateButtonView;
    private Button deleteButtonView;
    private TextView updateErrorView;
    private View updateProgressView;
    private boolean onProgress = false;
    private AlertDialog deleteDialog;
    private int userId;

    public AccountSettingsFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_account_settings, container, false);
    }


    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userId = SharedPreferencesManager.getUserId(getActivity());

        updateProgressView = view.findViewById(R.id.update_progress);
        updateProgressView.setVisibility(View.INVISIBLE);

        updateButtonView = view.findViewById(R.id.update_button);

        updateErrorView = view.findViewById(R.id.update_error);
        updateErrorView.setVisibility(View.INVISIBLE);
        deleteButtonView = view.findViewById(R.id.delete_button);

        firstNameView = view.findViewById(R.id.first_name);
        lastNameView = view.findViewById(R.id.last_name);
        emailView = view.findViewById(R.id.email);
        newPasswordView = view.findViewById(R.id.new_password);
        confirmNewPasswordView = view.findViewById(R.id.confirm_new_password);
        currentPasswordView = view.findViewById(R.id.current_password);
        
        deleteDialog = createDeleteDialog();
        deleteDialog.setCanceledOnTouchOutside(true);

        // insert current user account data
        onProgress = true;
        insertCurrentUserData();

        // setup listeners
        updateButtonView.setOnClickListener(v -> update());
        deleteButtonView.setOnClickListener(v -> deleteDialog.show());
    }

    /**
     * Creates a delete dialog to ask the user if he/she really wants to delete the account-
     */
    private AlertDialog createDeleteDialog() {

        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
        builder.setMessage(R.string.ask_delete)
                .setPositiveButton(R.string.delete_yes, (dialog, id) -> deleteUser())
                .setNegativeButton(R.string.delete_no, (dialog, id) -> {
                    dialog.cancel();
                });
        return builder.create();
    }


    /**
     * Deletes the user's account by doing an API call.
     */
    public void deleteUser() {
        if (onProgress) {
            return;
        }
        onProgress = true;

        updateProgressView.setVisibility(View.VISIBLE);
        ApiCreator.getApiService(getActivity()).deleteUser(userId).enqueue(new Callback<UserId>() {
            @Override
            public void onResponse(Call<UserId> call, Response<UserId> response) {
                if (response.isSuccessful()) {
                    SharedPreferencesManager.clearPreferences(getActivity());
                    startLoginActivity();
                } else {
                    updateProgressView.setVisibility(View.GONE);
                    updateErrorView.setText(getString(R.string.delete_error));
                    updateErrorView.setVisibility(View.VISIBLE);
                    onProgress = false;
                }
            }

            @Override
            public void onFailure(Call<UserId> call, Throwable t) {
                updateProgressView.setVisibility(View.GONE);
                updateErrorView.setText(getString(R.string.delete_error_http));
                updateErrorView.setVisibility(View.VISIBLE);
                onProgress = false;
            }
        });

    }

    /**
     * Sets current user data into text views.
     */
    public void setCurrentUserData() {
        firstNameView.setText(currentFirstName);
        lastNameView.setText(currentLastName);
        emailView.setText(currentEmail);
        onProgress = false;
    }

    /**
     * Checks data inserted for updating the user and modifies the layout accordingly
     */
    private void update() {

        if (onProgress) {
            return;
        }

        onProgress = true;

        Utils.hideKeyboardOnSubmit(getActivity());

        firstNameView.setError(null);
        lastNameView.setError(null);
        emailView.setError(null);
        newPasswordView.setError(null);
        confirmNewPasswordView.setError(null);
        currentPasswordView.setError(null);
        updateProgressView.setVisibility(View.VISIBLE);

        String firstName = firstNameView.getText().toString();
        String lastName = lastNameView.getText().toString();
        String email = emailView.getText().toString();
        String newPassword = newPasswordView.getText().toString();
        String confirmNewPassword = confirmNewPasswordView.getText().toString();
        String currentPassword = currentPasswordView.getText().toString();

        boolean cancel = false;
        View focusView = null;

        if (TextUtils.isEmpty(currentPassword)) {
            currentPasswordView.setError(getString(R.string.empty_error));
            focusView = currentPasswordView;
            cancel = true;
        } else {

            if (!(TextUtils.isEmpty(newPassword) && TextUtils.isEmpty(confirmNewPassword))) {

                if (TextUtils.isEmpty(confirmNewPassword)) {
                    confirmNewPasswordView.setError(getString(R.string.empty_error));
                    focusView = confirmNewPasswordView;
                    cancel = true;
                } else if (!AccountChecker.doPasswordsMatch(newPassword, confirmNewPassword)) {
                    confirmNewPasswordView.setError(getString(R.string.password_match_error));
                    focusView = confirmNewPasswordView;
                    cancel = true;
                }

                if (TextUtils.isEmpty(newPassword)) {
                    newPasswordView.setError(getString(R.string.empty_error));
                    focusView = newPasswordView;
                    cancel = true;
                } else if (!AccountChecker.isValidPassword(newPassword)) {
                    newPasswordView.setError(getString(R.string.password_error));
                    focusView = newPasswordView;
                    cancel = true;
                }
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
            } else if (!AccountChecker.isValidName(lastName)) {
                lastNameView.setError(getString(R.string.name_error));
                focusView = firstNameView;
                cancel = true;
            }


            if (TextUtils.isEmpty(firstName)) {
                firstNameView.setError(getString(R.string.empty_error));
                focusView = firstNameView;
                cancel = true;
            } else if (!AccountChecker.isValidName(firstName)) {
                firstNameView.setError(getString(R.string.name_error));
                focusView = firstNameView;
                cancel = true;
            }
        }

        if (cancel) {
            updateProgressView.setVisibility(View.GONE);
            focusView.requestFocus();
            onProgress = false;
        } else {
            tryUpdateUser(firstName, lastName, email, currentPassword, newPassword);
        }


    }


    /**
     * Checks if the old user password is correct and starts the update process
     */
    private void tryUpdateUser(String firstName, String lastName, String email, String currentPassword, String newPassword) {
        Context context = getActivity();

        String hashedPassword = SharedPreferencesManager.getPassword(context);

        if (!hashedPassword.equals("")) {
            if (hashedPassword.equals(SharedPreferencesManager.hashPassword(currentPassword))){
                updateUser(firstName, lastName, email,
                        newPassword.equals("") ? currentPassword : newPassword);
                return;
            }
        }
        updateProgressView.setVisibility(View.GONE);
        updateErrorView.setText(getString(R.string.update_error_invalid_password));
        updateErrorView.setVisibility(View.VISIBLE);
        onProgress=false;
    }

    /**
     * Updates the user account by doing an API call
     */
    public void updateUser(String firstName, String lastName, String email, String password) {
        ApiCreator.getApiService(getContext()).modifyUser(new User(firstName, lastName, email, password), SharedPreferencesManager.getUserId(getContext()))
                .enqueue(new Callback<UserId>() {
            @Override
            public void onResponse(Call<UserId> call, Response<UserId> response) {
                updateProgressView.setVisibility(View.GONE);
                if (response.isSuccessful()) {
                    SharedPreferencesManager.storePassword(getActivity(), password);
                    startHomeActivity();
                } else {
                    updateErrorView.setText(getString(R.string.update_error));
                    updateErrorView.setVisibility(View.VISIBLE);
                    updateProgressView.setVisibility(View.GONE);
                    onProgress = false;
                    ToastLauncher.showConnectionError(getContext());
                }

            }

            @Override
            public void onFailure(Call<UserId> call, Throwable t) {
                updateProgressView.setVisibility(View.GONE);
                updateErrorView.setText(getString(R.string.update_error_html));
                updateErrorView.setVisibility(View.VISIBLE);
                onProgress=false;
                ToastLauncher.showConnectionError(getContext());
            }
        });
    }

    /**
     * Insert current user data into layout fields by doing an API call
     */
    public void insertCurrentUserData() {
        Context context = getActivity();

        ApiCreator.getApiService(context).getUser(SharedPreferencesManager.getUserId(context)).enqueue(new Callback<UserResource>() {
            @Override
            public void onResponse(Call<UserResource> call, Response<UserResource> response) {
                if (response.isSuccessful()) {
                    UserResource user = response.body();
                    String firstName = user.getFirstName();
                    String lastName = user.getLastName();
                    String email = user.getEmail();
                    currentFirstName = firstName;
                    currentLastName = lastName;
                    currentEmail = email;
                    setCurrentUserData();
                } else {
                    setConnectionError();
                    ToastLauncher.showConnectionError(getContext());
                }
            }

            @Override
            public void onFailure(Call<UserResource> call, Throwable t) {
                setConnectionError();
            }
        });
    }

    public void startLoginActivity() {
        Intent intent = new Intent(getActivity(), LoginActivity.class);
        startActivity(intent);
    }

    public void setConnectionError() {
        updateErrorView.setText(getString(R.string.connection_error));
        updateErrorView.setVisibility(View.VISIBLE);
        onProgress=false;
    }
    public void startHomeActivity() {
        Intent intent = new Intent(getActivity(), HomeActivity.class);
        startActivity(intent);
    }
}
