package com.polimi.travlendar.home;


import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Switch;
import android.widget.TextView;

import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.PersonalVehicle;
import com.polimi.travlendar.api.pojos.Preferences;
import com.polimi.travlendar.api.pojos.UserId;
import com.polimi.travlendar.data.SharedPreferencesManager;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;


public class PreferencesFragment extends Fragment {

    private Switch busSwitchView;
    private Switch subwaySwitchView;
    private Switch trainSwitchView;
    private Switch tramSwitchView;
    private Switch carSwitchView;
    private Switch walkingSwitchView;
    private Switch bikeSwitchView;
    private Switch taxiSwitchView;
    private Switch enjoySwitchView;
    private Switch mobikeSwitchView;
    private TextView preferencesErrorView;
    private Button preferencesButtonView;
    private View preferencesProgressView;
    private boolean onProgress = false;
    private List<Switch> vehicleSwitches;
    private int userId;


    public PreferencesFragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_preferences, container, false);
    }

    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userId = SharedPreferencesManager.getUserId(getContext());

        preferencesProgressView = view.findViewById(R.id.preferences_progress);
        preferencesProgressView.setVisibility(View.INVISIBLE);

        preferencesButtonView = view.findViewById(R.id.preferences_button);

        preferencesErrorView = view.findViewById(R.id.preferences_error);
        preferencesErrorView.setVisibility(View.INVISIBLE);

        vehicleSwitches = new ArrayList<>();

        busSwitchView = view.findViewById(R.id.bus_switch);
        vehicleSwitches.add(busSwitchView);

        subwaySwitchView = view.findViewById(R.id.subway_switch);
        vehicleSwitches.add(subwaySwitchView);

        trainSwitchView = view.findViewById(R.id.train_switch);
        vehicleSwitches.add(trainSwitchView);

        tramSwitchView = view.findViewById(R.id.tram_switch);
        vehicleSwitches.add(tramSwitchView);

        carSwitchView = view.findViewById(R.id.car_switch);
        vehicleSwitches.add(carSwitchView);

        walkingSwitchView = view.findViewById(R.id.walking_switch);
        vehicleSwitches.add(walkingSwitchView);

        bikeSwitchView = view.findViewById(R.id.bike_switch);
        vehicleSwitches.add(bikeSwitchView);

        taxiSwitchView = view.findViewById(R.id.taxi_switch);
        vehicleSwitches.add(taxiSwitchView);

        enjoySwitchView = view.findViewById(R.id.enjoy_switch);
        vehicleSwitches.add(enjoySwitchView);

        mobikeSwitchView = view.findViewById(R.id.mobike_switch);
        vehicleSwitches.add(mobikeSwitchView);


        onProgress = true;
        insertCurrentUserPreferences();

        // set listeners
        preferencesButtonView.setOnClickListener(view1-> updatePreferences());
    }

    /**
     * Inserts current user global preferences in the layout
     */
    private void insertCurrentUserPreferences() {
        ApiCreator.getApiService(getContext()).getPreferences(userId).enqueue(new Callback<Preferences>() {
            @Override
            public void onResponse(Call<Preferences> call, Response<Preferences> response) {
                if (response.isSuccessful()) {
                    List<String> vehicles = response.body().getVehicles();

                    for (Switch s: vehicleSwitches) {
                        if (vehicles.contains(s.getText().toString().toLowerCase())) {
                            s.setChecked(true);
                        } else {
                            s.setChecked(false);
                        }
                    }

                    onProgress = false;
                } else {
                    setConnectionError();
                    ToastLauncher.showConnectionError(getContext());
                }
            }

            @Override
            public void onFailure(Call<Preferences> call, Throwable t) {
                setConnectionError();
                ToastLauncher.showConnectionError(getContext());
            }
        });
    }

    public void startHomeActivity() {
        Intent intent = new Intent(getActivity(), HomeActivity.class);
        startActivity(intent);
    }


    /**
     * Updates the user global preferences by doing an API call.
     */
    private void updatePreferences() {

        if (onProgress) {
            return;
        }
        onProgress = true;

        preferencesProgressView.setVisibility(View.VISIBLE);
        List<String> newPreferences = new ArrayList<>();

        for (Switch s: vehicleSwitches) {
            if (s.isChecked()) {
                newPreferences.add(s.getText().toString().toLowerCase());
            }
        }

        if (newPreferences.isEmpty()) {
            preferencesProgressView.setVisibility(View.GONE);
            preferencesErrorView.setText(getText(R.string.preferences_error_invalid));
            preferencesErrorView.setVisibility(View.VISIBLE);
            onProgress = false;
        } else {
            List<PersonalVehicle> personalVehicleList = new ArrayList<>();
            Preferences preferences = new Preferences(personalVehicleList, newPreferences);

            ApiCreator.getApiService(getActivity()).modifyPreferences(preferences, SharedPreferencesManager.getUserId(getActivity())).enqueue(new Callback<UserId>() {
                @Override
                public void onResponse(Call<UserId> call, Response<UserId> response) {
                    preferencesProgressView.setVisibility(View.GONE);
                    if (response.isSuccessful()) {
                        startHomeActivity();
                    } else {
                        preferencesErrorView.setText(getString(R.string.preferences_error_data));
                        preferencesErrorView.setVisibility(View.VISIBLE);
                        onProgress = false;
                    }
                }

                @Override
                public void onFailure(Call<UserId> call, Throwable t) {
                    preferencesProgressView.setVisibility(View.GONE);
                    preferencesErrorView.setText(R.string.preferences_error);
                    preferencesErrorView.setVisibility(View.VISIBLE);
                    onProgress = false;
                    ToastLauncher.showConnectionError(getContext());
                }
            });
        }

    }


    private void setConnectionError() {
        preferencesErrorView.setText(getString(R.string.connection_error));
        preferencesErrorView.setVisibility(View.VISIBLE);
        onProgress=false;
    }
}
