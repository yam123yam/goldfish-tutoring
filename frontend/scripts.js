// Define API endpoints
var API_REGISTER_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/register";
var API_LOGIN_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/login";
var API_AVAILABILITY_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/update/availability";
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
                    // Successful registration
                    document.getElementById("register_status").innerHTML = "Registration Successful!";
                    localStorage.setItem("username", inputData.username);
                    redirect_to_home(); // Redirect to home page after successful registration
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

//----for the calendar----//
document.addEventListener('DOMContentLoaded', function() {
    const daysTag = document.querySelector(".days");
    const currentDate = document.querySelector(".current-date");
    const prevNextIcon = document.querySelectorAll(".icons span");
    const availabilityData = document.getElementById("availabilityData");

    let date = new Date();
    let currYear = date.getFullYear();
    let currMonth = date.getMonth();

    const months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"];

    let availability = {};
    let selectedDays = [];

    const renderCalendar = () => {
        let firstDayofMonth = new Date(currYear, currMonth, 1).getDay();
        let lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate();
        let lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay();
        let lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate();
        let liTag = "";

        for (let i = firstDayofMonth; i > 0; i--) {
            liTag += `<li class="inactive">${lastDateofLastMonth - i + 1}</li>`;
        }

        for (let i = 1; i <= lastDateofMonth; i++) {
            let isToday = i === date.getDate() && currMonth === new Date().getMonth() 
                         && currYear === new Date().getFullYear() ? "active" : "";
            let isSelected = selectedDays.includes(`${currYear}-${currMonth+1}-${i}`) ? "selected" : "";
            liTag += `<li class="${isToday} ${isSelected}" data-date="${currYear}-${currMonth+1}-${i}">${i}</li>`;
        }

        for (let i = lastDayofMonth; i < 6; i++) {
            liTag += `<li class="inactive">${i - lastDayofMonth + 1}</li>`;
        }
        currentDate.innerText = `${months[currMonth]} ${currYear}`;
        daysTag.innerHTML = liTag;
    };

    // Initialize calendar
    renderCalendar();

    // Add event listeners to previous and next month buttons
    prevNextIcon.forEach(icon => {
        icon.addEventListener("click", () => {
            currMonth = icon.id === "prev" ? currMonth - 1 : currMonth + 1;

            if(currMonth < 0 || currMonth > 11) {
                date = new Date(currYear, currMonth, new Date().getDate());
                currYear = date.getFullYear();
                currMonth = date.getMonth();
            } else {
                date = new Date();
            }
            renderCalendar();
        });
    });

    let isDragging = false;

    // Add day selection functionality
    daysTag.addEventListener("mousedown", (e) => {
        if (e.target.tagName === "LI" && !e.target.classList.contains("inactive")) {
            isDragging = true;
            toggleSelection(e.target);
        }
    });

    daysTag.addEventListener("mousemove", (e) => {
        if (isDragging && e.target.tagName === "LI" && !e.target.classList.contains("inactive")) {
            toggleSelection(e.target);
        }
    });

    document.addEventListener("mouseup", () => {
        if (isDragging) {
            isDragging = false;
        }
    });

    const toggleSelection = (element) => {
        const date = element.dataset.date;
        if (element.classList.contains("selected")) {
            element.classList.remove("selected");
            selectedDays = selectedDays.filter(item => item !== date);
        } else {
            element.classList.add("selected");
            if (!selectedDays.includes(date)) {
                selectedDays.push(date);
            }
        }
    };

    document.getElementById("availability_submit").onclick = function() {
        const startTime = document.getElementById("startTime").value;
        const endTime = document.getElementById("endTime").value;
        const subjects = Array.from(document.querySelectorAll("#subjects option:checked")).map(option => option.value);
        const username = localStorage.getItem("username");

        if (selectedDays.length === 0) {
            document.getElementById("availability_status").innerHTML = "Please select at least one day";
            return;
        }

        if (startTime && endTime && subjects.length > 0) {
            selectedDays.forEach(day => {
                if (!availability[day]) {
                    availability[day] = [];
                }
                availability[day].push({ start: startTime, end: endTime });
            });

            // Convert subject array to format expected by Lambda
            const subjectsFormatted = subjects.map(subject => ({ S: subject }));
            
            // Convert availability object to format expected by Lambda
            const availabilityFormatted = Object.entries(availability).map(([date, times]) => {
                return {
                    M: {
                        date: { S: date },
                        times: { 
                            L: times.map(time => ({ 
                                M: {
                                    start: { S: time.start },
                                    end: { S: time.end }
                                }
                            }))
                        }
                    }
                };
            });

            const inputData = {
                username: { S: username },
                subjects: { L: subjectsFormatted },
                availability: { L: availabilityFormatted }
            };

            document.getElementById("availability_status").innerHTML = "Saving availability...";

            // Send AJAX request
            $.ajax({
                url: API_AVAILABILITY_ENDPOINT,
                type: "POST",
                data: JSON.stringify(inputData),
                contentType: "application/json",
                success: function(response) {
                    let res = typeof response === "string" ? JSON.parse(response) : response;
                    if (res.status === "success") {
                        document.getElementById("availability_status").innerHTML = "Availability saved successfully!";
                    } else {
                        document.getElementById("availability_status").innerHTML = "Error: " + res.message;
                    }
                },
                error: function(xhr, status, error) {
                    document.getElementById("availability_status").innerHTML = "Error saving availability. Please try again.";
                    console.error("Error:", xhr.responseText);
                }
            });

            // Clear selection
            selectedDays = [];
            renderCalendar();
            //displayAvailabilityData();
        } else {
            document.getElementById("availability_status").innerHTML = "Please fill all fields";
        }
    };

    const displayAvailabilityData = () => {
        availabilityData.textContent = JSON.stringify(availability, null, 2);
    };
});

// Navigation functions
function redirect_to_login() {
    window.location.href = "login.html";
}

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

function temp_json(temp_json_file) {
    let json_file = temp_json_file;
    return json_file;
}