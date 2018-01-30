package com.polimi.travlendar.api;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.polimi.travlendar.api.pojos.Jwt;
import com.polimi.travlendar.api.pojos.LoginUser;
import com.polimi.travlendar.api.pojos.User;
import com.polimi.travlendar.api.pojos.UserId;
import com.polimi.travlendar.api.pojos.UserResource;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import java.io.IOException;

import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;


/**
 * Tests the Retrofit client and the API by doing calls for the user resource.
 */
public class TravlendarApiTest {

    private static final String TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ";
    private static Gson gson = new GsonBuilder().create();
    private static MockWebServer mockedServer = new MockWebServer();
    private static String url = mockedServer.url("").toString();
    private static Retrofit retrofitClient;
    private static TravlendarApi api;

    private static final String TEST_FIRST_NAME = "test_first_name";
    private static final String TEST_LAST_NAME = "test_last_name";
    private static final String TEST_EMAIL = "test@test.it";

    private static final String TEST_PASSWORD = "test_password";

    @BeforeClass
    public static void setUp() {
        OkHttpClient client = new OkHttpClient.Builder().addInterceptor(new Interceptor() {
            @Override
            public Response intercept(Chain chain) throws IOException {
                Request newRequest = chain.request().newBuilder()
                        .addHeader("Authorization", "Bearer " + TOKEN)
                        .build();
                return chain.proceed(newRequest);
            }
        }).build();


        retrofitClient = new Retrofit.Builder()
                .client(client)
                .baseUrl(url)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build();

        api = retrofitClient.create(TravlendarApi.class);
    }



    @Test
    public void createUserTest() throws IOException, InterruptedException {

        mockedServer.enqueue(new MockResponse().setBody(gson.toJson(new UserId(1))));

        UserId userId = api.createUser(new User(
                TEST_FIRST_NAME, TEST_FIRST_NAME, TEST_EMAIL, TEST_PASSWORD
        )).execute().body();

        RecordedRequest request = mockedServer.takeRequest();
        assertEquals("/users", request.getPath());
        assertEquals(new Integer(1), userId.getId());
    }


    @Test
    public void getUserTest() throws IOException, InterruptedException {

        mockedServer.enqueue(new MockResponse().setBody(gson.toJson(new UserResource(
                TEST_FIRST_NAME,
                TEST_LAST_NAME,
                TEST_EMAIL
        ))));
        mockedServer.enqueue(new MockResponse().setResponseCode(404));

        UserResource userResource = api.getUser(1).execute().body();

        RecordedRequest request = mockedServer.takeRequest();
        assertEquals("/users/1", request.getPath());

        assertNotNull(request.getHeader("Authorization"));

        assertEquals(userResource.getFirstName(), TEST_FIRST_NAME);
        assertEquals(userResource.getLastName(), TEST_LAST_NAME);
        assertEquals(userResource.getEmail(), TEST_EMAIL);

        assertNotNull(api.getUser(2).execute().errorBody());

        RecordedRequest request1 = mockedServer.takeRequest();
        assertEquals("/users/2", request1.getPath());

    }

    @Test
    public void loginUserTest() throws IOException, InterruptedException {
        mockedServer.enqueue(new MockResponse().setBody(gson.toJson(new Jwt(1, TOKEN))));


        Jwt token = api.loginUser(new LoginUser(TEST_EMAIL, TEST_PASSWORD)).execute().body();

        assertEquals(TOKEN, token.getAuthToken());
        assertEquals(new Integer(1), token.getId());

        RecordedRequest request = mockedServer.takeRequest();
        assertEquals("/login", request.getPath());
    }

    @Test
    public void modifyUserTest() throws IOException, InterruptedException {

        mockedServer.enqueue(new MockResponse().setBody(gson.toJson(new UserId(1))));

        UserId userId = api.modifyUser(new User(
                TEST_FIRST_NAME, TEST_FIRST_NAME, TEST_EMAIL, TEST_PASSWORD
        ), 1).execute().body();

        RecordedRequest request = mockedServer.takeRequest();
        assertEquals("/users/1", request.getPath());
        assertEquals(new Integer(1), userId.getId());

        assertNotNull(request.getHeader("Authorization"));
    }

    @Test
    public void deleteUserTest() throws IOException, InterruptedException {

        mockedServer.enqueue(new MockResponse().setBody(gson.toJson(new UserId(1))));

        UserId userId = api.deleteUser(1).execute().body();

        RecordedRequest request = mockedServer.takeRequest();
        assertEquals("/users/1", request.getPath());
        assertEquals(new Integer(1), userId.getId());

        assertNotNull(request.getHeader("Authorization"));

    }

    @AfterClass
    public static void tearDown() throws IOException {
        mockedServer.shutdown();
    }
}