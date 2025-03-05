// Define API endpoints
var API_REGISTER_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/register";
var API_LOGIN_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/login";
var API_AVAILABILITY_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/schedule";
var API_GET_ROLE_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/role";

// Register user post request
function register_post_request() {
    document.getElementById("register_user").onclick = function() {
        var inputData = {
            "username": $('#username').val(),
            "password": $('#password').val(),
            "email": $('#email').val(),
            "phone_number": $('#phone_number').val(),
            "pet_name": $('#pet_name').val(),
            "role": $('#role').val(),
            "full_name": $('#full_name').val(),
            "grade": $('#grade').val()
        };

        // Send AJAX request
        $.ajax({
            url: API_REGISTER_ENDPOINT,
            type: 'POST',
            data: JSON.stringify(inputData),
            contentType: 'application/json; charset=utf-8',
            success: function(response) {
                // Check Lambda response status (assuming statusCode or message in the response)
                if (response.status === "success") {
                    // Successful login
                    document.getElementById("register_status").innerHTML = "Registration Successful!";
                    redirect_to_home(); // Redirect to home page after successful login
                } else {
                    // Handle specific error message from Lambda
                    document.getElementById("register_status").innerHTML = "Error: " + response.message;
                }
            },
            error: function() {
                document.getElementById("register_status").innerHTML = "Error in Registration";
            }
        });
    }
}

// login post request
function login_post_request() {
    document.getElementById("login_user").onclick = function(event) {
        //event.preventDefault(); // Prevent form submission
        var inputData = {
            "username": $('#username').val(),
            "password": $('#password').val()
        };

        // Send AJAX request
        $.ajax({
            url: API_LOGIN_ENDPOINT,
            type: 'POST',
            data: JSON.stringify(inputData),
            contentType: 'application/json; charset=utf-8',
            success: function(response) {
                // Check Lambda response status
                if (response.status === "success") {
                    // Successful login
                    localStorage.setItem("username", inputData.username);
                    get_role();
                } else {
                    // Handle specific error message from Lambda
                    document.getElementById("login_status").innerHTML = "Error: " + response.message;
                }
            },
            error: function(xhr, status, error) {
                // General error handling
                document.getElementById("login_status").innerHTML = "Error in Login. Please try again.";
            }
        });
    }
}


$(document).ready(function () {
    var calendarEl = document.getElementById("calendar");
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "timeGridWeek",
        selectable: true,
        select: function (info) {
            console.log("Selected:", info.start, info.end);
        }
    });
    calendar.render();

    // Save availability when the button is clicked
    $("#save_availability").click(function () {
        let username = localStorage.getItem("username");
        let selectedSubject = $("#subject").val();
        let events = calendar.getEvents().map(event => ({
            start: event.start.toISOString(),
            end: event.end.toISOString()
        }));

        let requestData = {
            username: username,
            subject: selectedSubject,
            availability: events
        };

        console.log("Sending data to API:", requestData);

        $.ajax({
            url: API_AVAILABILITY_ENDPOINT,
            type: "POST",
            data: JSON.stringify(requestData),
            contentType: "application/json",
            success: function (response) {
                let res = typeof response === "string" ? JSON.parse(response) : response;
                if (res.status === "success") {
                    document.getElementById("availability_status").innerHTML = "Availability saved successfully!";
                } else {
                    document.getElementById("availability_status").innerHTML = "Error: " + res.message;
                }
            },
            error: function (xhr, status, error) {
                document.getElementById("availability_status").innerHTML = "Error saving availability. Please try again.";
                console.error("Error:", xhr.responseText);
            }
        });
    });
});


function add_availability() {
    document.getElementById("save_availability").onclick = function(event) {
        var calendarEl = document.getElementById("calendar");
        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: "timeGridWeek",
            selectable: true,
            select: function (info) {
                console.log("Selected:", info.start, info.end);
            }
        });
        calendar.render();
    
        $("#save_availability").click(function () {
            let username = localStorage.getItem("username");
            let selectedSubject = $("#subject").val();
            let events = calendar.getEvents().map(event => ({
                start: event.start.toISOString(),
                end: event.end.toISOString()
            }));
    
            let requestData = {
                username: username,
                subject: selectedSubject, // Matches backend
                availability: events
            };
    
            console.log("Sending data to API:", requestData);
    
            $.ajax({
                url: API_AVAILABILITY_ENDPOINT,
                type: "POST",
                data: JSON.stringify(requestData),
                contentType: "application/json",
                success: function(response) {
                    let res = typeof response === "string" ? JSON.parse(response) : response;
                    if (res.status === "success") {
                        document.getElementById("availability_status").innerHTML = "Availability saved successfully!";
                    } else {
                        document.getElementById("availability_status_status").innerHTML = "Error: " + response.message;
                    }
                },
                error: function(xhr, status, error) {
                    document.getElementById("availability_status_status").innerHTML = "Error in Login. Please try again.";
                }
            });
        });
    };
}


    
// Function to navigate to login.html
function redirect_to_login() {
    window.location.href = "login.html";
}

// Function to navigate to home.html
function redirect_to_home() {
    window.location.href = "home.html";
}

function redirect_to_student_home() {
    window.location.href = "student_home.html";
}

function redirect_to_tutor_home() {
    window.location.href = "tutor_home.html";
}

function get_role() {
    let username = localStorage.getItem("username");

    $.ajax({
        url: API_GET_ROLE_ENDPOINT,
        type: "POST",
        data: JSON.stringify({ username: username }),
        contentType: "application/json",
        success: function(response) {
            if (response.role === "tutor") {
                redirect_to_tutor_home();
            } else {
                redirect_to_student_home();
            }
        },
        error: function(xhr, status, error) {
            console.log("Error getting role");
        }
    });
}

localStorage.setItem("username", enteredUsername);
//const userUUID = localStorage.getItem("uuid");
