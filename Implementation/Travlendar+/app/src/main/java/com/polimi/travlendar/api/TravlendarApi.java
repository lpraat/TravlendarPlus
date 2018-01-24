package com.polimi.travlendar.api;

import com.polimi.travlendar.api.pojos.AllCalendars;
import com.polimi.travlendar.api.pojos.Calendar;
import com.polimi.travlendar.api.pojos.CalendarId;
import com.polimi.travlendar.api.pojos.Event;
import com.polimi.travlendar.api.pojos.EventId;
import com.polimi.travlendar.api.pojos.EventResource;
import com.polimi.travlendar.api.pojos.Instructions;
import com.polimi.travlendar.api.pojos.Jwt;
import com.polimi.travlendar.api.pojos.LoginUser;
import com.polimi.travlendar.api.pojos.Preferences;
import com.polimi.travlendar.api.pojos.Recurrences;
import com.polimi.travlendar.api.pojos.User;
import com.polimi.travlendar.api.pojos.UserId;
import com.polimi.travlendar.api.pojos.UserResource;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.PUT;
import retrofit2.http.Path;


/**
 * This interface will be used by retrofit client to do REST API calls.
 * Request and response body are properly encoded/decoded by retrofit using Json/pojo.
 */
public interface TravlendarApi {

    @POST("/users")
    Call<UserId> createUser(@Body User user);

    @GET("/users/{id}")
    Call<UserResource> getUser(@Path("id") int userId);

    @POST("/login")
    Call<Jwt> loginUser(@Body LoginUser loginUser);

    @PUT("/users/{id}")
    Call<UserId> modifyUser(@Body User user, @Path("id") int userId);

    @DELETE("/users/{id}")
    Call<UserId> deleteUser(@Path("id") int userId);

    @GET("/users/{id}/preferences")
    Call<Preferences> getPreferences(@Path("id") int userId);

    @PUT("/users/{id}/preferences")
    Call<UserId> modifyPreferences(@Body Preferences preferences, @Path("id") int userId);

    @POST("/users/{id}/calendars")
    Call<CalendarId> createCalendar(@Body Calendar calendar, @Path("id") int userId);

    @PUT("/users/{id}/calendars/{calendar_id}")
    Call<CalendarId> modifyCalendar(@Body Calendar calendar, @Path("id") int userId, @Path("calendar_id") int calendarId);

    @DELETE("/users/{id}/calendars/{calendar_id}")
    Call<CalendarId> deleteCalendar(@Path("id") int userId, @Path("calendar_id") int calendarId);

    @GET("/users/{id}/calendars")
    Call<AllCalendars> getAllCalendars(@Path("id") int userId);

    @GET("/users/{id}/calendars/{calendar_id}")
    Call<Calendar> getCalendar(@Path("id") int userId, @Path("calendar_id") int calendarId);

    @GET("/users/{id}/schedule")
    Call<Recurrences> getSchedule(@Path("id") int userId);

    @POST("/users/{id}/calendars/{calendar_id}/events")
    Call<EventId> createEvent(@Body Event event, @Path("id") int userId, @Path("calendar_id") int calendarId);

    @GET("/users/{id}/calendars/{calendar_id}/events/{event_id}")
    Call<EventResource> getEvent(@Path("id") int userId, @Path("calendar_id") int calendarId, @Path("event_id") int eventId);

    @PUT("/users/{id}/calendars/{calendar_id}/events/{event_id}")
    Call<EventId> modifyEvent(@Body Event event, @Path("id") int userId, @Path("calendar_id") int calendarId, @Path("event_id") int eventId);

    @DELETE("/users/{id}/calendars/{calendar_id}/events/{event_id}")
    Call<EventId> deleteEvent(@Path("id") int userId, @Path("calendar_id") int calendarId, @Path("event_id") int eventId);

    @DELETE("/users/{id}/calendars/{calendar_id}/events/{event_id}/recurrences/{recurrence_id}")
    Call<EventId> deleteRecurrence(@Path("id") int userId, @Path("calendar_id") int calendarId, @Path("event_id") int eventId, @Path("recurrence_id") int recurrenceId);

    @GET("/users/{id}/calendars/{calendar_id}/events/{event_id}/recurrence/{recurrence_id}/instruction")
    Call<Instructions> getInstructions(@Path("id") int userId, @Path("calendar_id") int calendarId, @Path("event_id") int eventId, @Path("recurrence_id") int recurrenceId);

    @GET("/users/{id}/calendars/{calendar_id}/events/{event_id}/recurrence/{recurrence_id}/return")
    Call<Instructions> getReturnInstructions(@Path("id") int userId, @Path("calendar_id") int calendarId, @Path("event_id") int eventId, @Path("recurrence_id") int recurrenceId);


}

