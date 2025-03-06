// Define API endpoints
var API_REGISTER_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/register";
var API_LOGIN_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/login";
var API_AVAILABILITY_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/update/availability";
var API_GET_ROLE_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/role";
var API_GET_TUTORS_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/session/get_tutors"
var API_FETCH_USER_DATA_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/users/fetch_data";
var API_UPDATE_PROFILE_ENDPOINT = "https://p5r4ervae0.execute-api.us-east-2.amazonaws.com/dev/update/profile"


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

//scheduling a session 
document.addEventListener('DOMContentLoaded', function() {
    // Get the elements
    const scheduleButton = document.getElementById('schedule_sess_btn');
    const subjectSelect = document.getElementById('subject');
    const dateInput = document.getElementById('date');
    const timeInput = document.getElementById('time');
    const statusElement = document.getElementById('session_status');
    const dataElement = document.getElementById('sesh_data');

    // Add click event listener to the schedule button
    scheduleButton.addEventListener('click', scheduleSession);

    // Function to schedule a session
    function scheduleSession() {
        // Clear previous messages
        statusElement.textContent = '';
        dataElement.innerHTML = '';

        // Validate inputs
        if (!subjectSelect.value || !dateInput.value || !timeInput.value) {
            statusElement.textContent = 'Please fill in all fields.';
            return;
        }
    
        // Show loading message
        statusElement.textContent = 'Searching for available tutors...';

        // Prepare data for the API call
        const sessionData = {
            subject: subjectSelect.value,
            date: dateInput.value,
            time: timeInput.value
        };

        // Make the API call to AWS Lambda
        $.ajax({
            url: API_GET_TUTORS_ENDPOINT,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(sessionData),
            success: function(response) {
                handleScheduleResponse(response);
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                let errorMsg = 'An error occurred while scheduling the session.';
                
                // Try to parse the error response for more details
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    if (errorResponse.error) {
                        errorMsg = errorResponse.error;
                    }
                } catch (e) {
                    // If parsing fails, use the default error message
                }
                
                statusElement.textContent = errorMsg;
            }
        });
    }

    // Function to handle the API response
    function handleScheduleResponse(response) {
        // Clear the status message
        statusElement.textContent = '';

        // Check if response contains a status code (API Gateway format)
        if (response.statusCode) {
            const responseBody = JSON.parse(response.body);
            
            if (response.statusCode === 200) {
                displayTutors(responseBody.tutors);
            } else {
                statusElement.textContent = responseBody.error || 'No tutors available for the selected criteria.';
            }
        } 
        // Direct lambda function response format
        else if (response.status === 'success') {
            displayTutors(response.tutors);
        } else {
            statusElement.textContent = response.message || 'No tutors available for the selected criteria.';
        }
    }

    // Function to display the list of tutors
    function displayTutors(tutors) {
        if (!tutors || tutors.length === 0) {
            statusElement.textContent = 'No tutors available for the selected criteria.';
            return;
        }

        // Create a header for the data section
        const header = document.createElement('h3');
        header.textContent = 'Available Tutors:';
        dataElement.appendChild(header);

        // Create a table for the tutors
        const table = document.createElement('table');
        table.classList.add('tutor-table');
        
        // Add table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        ['Name', 'Email', 'Phone', 'Subjects', 'Select'].forEach(text => {
            const th = document.createElement('th');
            th.textContent = text;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Add table body with tutor data
        const tbody = document.createElement('tbody');
        tutors.forEach(tutor => {
            const row = document.createElement('tr');
            
            // Add tutor information
            addTableCell(row, tutor.username);
            addTableCell(row, tutor.email);
            addTableCell(row, tutor.phone_number || 'N/A');
            addTableCell(row, Array.isArray(tutor.subjects) ? tutor.subjects.join(', ') : tutor.subjects);
            
            // Add selection button
            const selectCell = document.createElement('td');
            const selectButton = document.createElement('button');
            selectButton.textContent = 'Select';
            selectButton.classList.add('select-btn');
            selectButton.dataset.username = tutor.username;
            selectButton.addEventListener('click', function() {
                selectTutor(tutor);
            });
            selectCell.appendChild(selectButton);
            row.appendChild(selectCell);
            
            tbody.appendChild(row);
        });
        table.appendChild(tbody);
        dataElement.appendChild(table);

        // Display available tutors in the status element
        statusElement.textContent = `Available Tutors: ${tutors.map(tutor => tutor.username).join(', ')}`;
    }

    // Helper function to add a cell to a table row
    function addTableCell(row, text) {
        const cell = document.createElement('td');
        cell.textContent = text || 'N/A';
        row.appendChild(cell);
    }

    // Function to handle tutor selection
    function selectTutor(tutor) {
        // Clear previous content
        dataElement.innerHTML = '';
        
        // Create confirmation message
        const confirmation = document.createElement('div');
        confirmation.classList.add('confirmation');
        
        const message = document.createElement('p');
        message.textContent = `You've selected ${tutor.username} for a ${subjectSelect.value} session on ${formatDate(dateInput.value)} at ${formatTimeForDisplay(timeInput.value)}.`;
        confirmation.appendChild(message);
        
        // Create confirm button
        const confirmButton = document.createElement('button');
        confirmButton.textContent = 'Confirm Booking';
        confirmButton.classList.add('btn');
        confirmButton.addEventListener('click', function() {
            confirmBooking(tutor);
        });
        confirmation.appendChild(confirmButton);
        
        // Create back button
        const backButton = document.createElement('button');
        backButton.textContent = 'Back to Tutor List';
        backButton.classList.add('btn', 'secondary');
        backButton.addEventListener('click', function() {
            scheduleSession(); // This will re-fetch the tutor list
        });
        confirmation.appendChild(backButton);
        
        dataElement.appendChild(confirmation);
    }

    // Function to confirm booking
    function confirmBooking(tutor) {
        // Here you would call another API to save the booking
        // For now, we'll just show a success message
        dataElement.innerHTML = '';
        
        const success = document.createElement('div');
        success.classList.add('success-message');
        
        const message = document.createElement('p');
        message.textContent = `Your session with ${tutor.username} has been booked successfully! You will receive a confirmation email shortly.`;
        success.appendChild(message);
        
        dataElement.appendChild(success);
        
        // Reset the form after a short delay
        setTimeout(function() {
            subjectSelect.selectedIndex = 0;
            dateInput.value = '';
            timeInput.value = '';
        }, 3000);
    }

    // Helper function to format time from HTML time input to API format
    function formatTimeForAPI(timeStr) {
        // Convert from 24-hour format to 12-hour format with AM/PM
        if (!timeStr) return '';
        
        const [hours, minutes] = timeStr.split(':');
        let hour = parseInt(hours, 10);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        
        // Convert to 12-hour format
        hour = hour % 12;
        hour = hour ? hour : 12; // Convert 0 to 12
        
        return `${hour}:${minutes} ${ampm}`;
    }

    // Helper function to format time for display
    function formatTimeForDisplay(timeStr) {
        // Already in display format from the time input
        return timeStr;
    }

    // Helper function to format date for display
    function formatDate(dateStr) {
        if (!dateStr) return '';
        
        const date = new Date(dateStr);
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }
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

ocument.addEventListener('DOMContentLoaded', function() {
    const profileDetailsElement = document.getElementById('profile-details');
    const username = localStorage.getItem('username');

    if (username) {
        fetchUserData(username).then(userData => {
            displayUserProfile(userData);
        }).catch(error => {
            console.error('Error fetching user data:', error);
        });

        document.getElementById('update_button').addEventListener('click', function() {
            saveProfile();
        });
    } else {
        console.error('No username found in localStorage');
    }
});

function fetchUserData(username) {
    return fetch(API_FETCH_USER_DATA_ENDPOINT, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        return JSON.parse(data.body);
    })
    .catch(error => {
        throw new Error('Error fetching user data: ' + error.message);
    });
}

function displayUserProfile(userData) {
    const profileDetailsElement = document.getElementById('profile-details');
    if (profileDetailsElement) {
        profileDetailsElement.innerHTML = `
            <p><strong>Full Name:</strong> ${userData.full_name}</p>
            <p><strong>Email:</strong> ${userData.email}</p>
            <p><strong>Grade:</strong> ${userData.grade}</p>
            <p><strong>Phone Number:</strong> ${userData.phone_number}</p>
        `;
    } else {
        populateEditProfileForm(userData);
    }
}

function populateEditProfileForm(userData) {
    document.getElementById('full_name').value = userData.full_name;
    document.getElementById('email').value = userData.email;
    document.getElementById('username').value = userData.username;
    document.getElementById('grade').value = userData.grade;
    document.getElementById('phone_number').value = userData.phone_number;
    document.getElementById('pet_name').value = userData.pet_name;
}

function saveProfile() {
    
    var username = localStorage.getItem('username')

    const updatedUserData = {
        username: username,
        full_name: document.getElementById('full_name').value,
        email: document.getElementById('email').value,
        grade: document.getElementById('grade').value,
        phone_number: document.getElementById('phone_number').value,
    };

    fetch(API_UPDATE_PROFILE_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedUserData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('profile_status').textContent = 'Profile updated successfully!';
        window.location.href = "profile.html";
    })
    .catch(error => {
        console.error('Error updating profile:', error);
        document.getElementById('profile_status').textContent = 'Error updating profile';
    });
}