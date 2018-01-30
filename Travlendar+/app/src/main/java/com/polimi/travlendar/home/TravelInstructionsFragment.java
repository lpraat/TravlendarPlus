package com.polimi.travlendar.home;


import android.graphics.Color;
import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v4.app.Fragment;
import android.text.Html;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.ScrollView;
import android.widget.TextView;

import com.google.android.gms.maps.CameraUpdate;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.PolylineOptions;
import com.google.maps.android.PolyUtil;
import com.polimi.travlendar.R;
import com.polimi.travlendar.ToastLauncher;
import com.polimi.travlendar.Utils;
import com.polimi.travlendar.api.ApiCreator;
import com.polimi.travlendar.api.pojos.Instructions;
import com.polimi.travlendar.api.pojos.Overview;
import com.polimi.travlendar.api.pojos.Step;
import com.polimi.travlendar.data.SharedPreferencesManager;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class TravelInstructionsFragment extends Fragment {

    public static final String CALENDAR_ID = "calendar_id";
    public static final String EVENT_ID = "event_id";
    public static final String RECURRENCE_ID = "recurrence_id";
    private GScrollableMap gScrollableMap;
    private GScrollableMap gScrollableMapReturn;
    private ScrollView scrollView;
    private TextView instructionsText;
    private ImageView warningView;
    private TextView warningTextView;
    private TextView returnTextView;
    private TextView instructionsReturnText;
    int userId;
    int calendarId;
    int eventId;
    int recurrenceId;



    public TravelInstructionsFragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_travel_instructions, container, false);
    }

    @Override
    public void onViewCreated(View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        userId = SharedPreferencesManager.getUserId(getContext());
        calendarId = getArguments().getInt(CALENDAR_ID);
        eventId = getArguments().getInt(EVENT_ID);
        recurrenceId = getArguments().getInt(RECURRENCE_ID);

        warningView = view.findViewById(R.id.warning);
        warningTextView = view.findViewById(R.id.warning_text);
        instructionsText = view.findViewById(R.id.directions);
        scrollView = view.findViewById(R.id.scroll_view);

        returnTextView = view.findViewById(R.id.return_text);
        returnTextView.setVisibility(View.GONE);
        instructionsReturnText = view.findViewById(R.id.directions_return);




        if (gScrollableMap == null) {
            gScrollableMap = ((GScrollableMap) getChildFragmentManager().findFragmentById(R.id.map));

            // set listeners
            gScrollableMap.setListener(() -> scrollView.requestDisallowInterceptTouchEvent(true));

        }

        if (gScrollableMapReturn == null) {
            gScrollableMapReturn = ((GScrollableMap) getChildFragmentManager().findFragmentById(R.id.map_return));
            gScrollableMapReturn.getView().setVisibility(View.GONE);

            // set listeners
            gScrollableMapReturn.setListener(() -> scrollView.requestDisallowInterceptTouchEvent(true));

        }


        // api call for getting the instruction of this event and drawing the map
        ApiCreator.getApiService(getContext()).getInstructions(userId, calendarId, eventId, recurrenceId).enqueue(new Callback<Instructions>() {
            @Override
            public void onResponse(Call<Instructions> call, Response<Instructions> response) {
                if (response.isSuccessful()) {
                    drawMap(response.body(), gScrollableMap, instructionsText);
                } else {
                    ToastLauncher.instructionsError(getContext());
                }
            }

            @Override
            public void onFailure(Call<Instructions> call, Throwable t) {
                ToastLauncher.showConnectionError(getContext());
            }
        });

        ApiCreator.getApiService(getContext()).getReturnInstructions(userId, calendarId, eventId, recurrenceId).enqueue(new Callback<Instructions>() {
            @Override
            public void onResponse(Call<Instructions> call, Response<Instructions> response) {
                if (response.isSuccessful()) {
                    returnTextView.setVisibility(View.VISIBLE);
                    gScrollableMapReturn.getView().setVisibility(View.VISIBLE);
                    drawMap(response.body(), gScrollableMapReturn, instructionsReturnText);
                }
            }

            @Override
            public void onFailure(Call<Instructions> call, Throwable t) {
                ToastLauncher.showConnectionError(getContext());
            }
        });


    }

    /**
     * Draws the instructions retrieved in a google map.
     * An instruction is made by 2 marker indicating the start and the end of the travel
     * and by a polyline, the line indicating the set of latitude/longitude pairs in the travel.
     * There are also a set of directions given to the user that are showed under the map and are
     * populated by this function.
     * @param instructions the instructions retrieved from the travlendar API.
     */
    public void drawMap(Instructions instructions, GScrollableMap gScrollableMap, TextView directions) {
        gScrollableMap.getMapAsync(googleMap -> {

            Overview overview = instructions.getOverview();

            List<Step> steps = instructions.getSteps();

            LatLng start = new LatLng(overview.getStartLat(), overview.getStartLng());
            LatLng end = new LatLng(overview.getEndLat(), overview.getEndLng());

            MarkerOptions markerStart = new MarkerOptions().position(start);
            MarkerOptions markerEnd = new MarkerOptions().position(end);
            googleMap.addMarker(markerStart.title("Start"));
            googleMap.addMarker(markerEnd.title("End"));

            PolylineOptions options = new PolylineOptions().width(5).color(Color.BLUE);


            int seconds = overview.getDuration();
            int meters = overview.getDistance();

            int hour = seconds / 3600;
            int minute = (seconds % 3600) / 60;
            String totalTravelTime = Utils.getDateString(hour, minute);

            String travelMode = steps.get(0).getTravelMode();
            directions.append("Total travel time in hours and minutes: " + totalTravelTime);
            directions.append("\n");
            directions.append("Total travel meters: " + meters);
            directions.append("\n");
            directions.append(Html.fromHtml("<h2>" + travelMode + "</h2>"));

            for (Step s: steps) {
                List<LatLng> latLngList = PolyUtil.decode(s.getPolyline());

                for (LatLng latLng :latLngList) {
                    options.add(latLng);
                }

                if (!s.getTravelMode().equals(travelMode)) { // this step includes a different travel mode
                    String newTravelMode = s.getTravelMode();
                    directions.append("\n");
                    appendFromHtml("<h2>" + newTravelMode + "</h2>", directions);
                    directions.append("\n");
                }
                appendFromHtml(s.getInstructions(), directions);
                directions.append("\n");
            }
            googleMap.addPolyline(options);

            LatLngBounds.Builder builder = new LatLngBounds.Builder();
            builder.include(markerStart.getPosition());
            builder.include(markerEnd.getPosition());
            int width = getResources().getDisplayMetrics().widthPixels;
            int height = getResources().getDisplayMetrics().heightPixels;
            int padding = (int) (width * 0.10); // offset from edges of the map 10% of screen
            CameraUpdate cu = CameraUpdateFactory.newLatLngBounds(builder.build(), width, height, padding);
            googleMap.moveCamera(cu);

            if (!overview.getReachable()) {
                warningView.setVisibility(View.VISIBLE);
                warningTextView.setVisibility(View.VISIBLE);
            }
        });

    }

    /**
     * Append in the instructions text view the directions.
     */
    private void appendFromHtml(String data, TextView directions) {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
            directions.append(Html.fromHtml(data,Html.FROM_HTML_MODE_LEGACY));
        } else {
            directions.append(Html.fromHtml(data));
        }
    }
}
