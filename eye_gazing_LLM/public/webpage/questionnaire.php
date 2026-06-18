<?php
// Load config to set up session and authentication  
include '../../src/init/config.php';

// Check if user is authenticated, redirect to login if not
checkUserAuthentication();
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/questionnaire.css">
        <link rel="stylesheet" href="/public/css/general.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <script type="module" src="/public/js/events/questionnaire.js" defer></script>
    <script type='module' src='../js/functions/timeout.js' defer></script>

    <body>
        <div> 
            <div>
                <h2>Questionnaire</h2>
                <form id="questionnaire-form" action="questionnaire.php" method="POST">

                    <div class="form-group">
                        <label for="age">Age: </label>
                        <input id="age" name="age" type="number" min="0" required maxlength="3">
                    </div> 
                    
                    <div class="form-group">
                        <label for="location">Location (e.g., California): </label>
                        <input id="location" name="location" type="text" required maxlength="250">
                    </div>

                    <label>Highest Education Level:</label><br>
                    <input id="education1" name="education" type="radio" value="High School Graduate" required>
                    <label for="education1">High School Graduate</label><br>

                    <input id="education2" name="education" type="radio" value="Associate">
                    <label for="education2">Associate</label><br>

                    <input id="education3" name="education" type="radio" value="Bachelor">
                    <label for="education3">Bachelor</label><br>

                    <input id="education4" name="education" type="radio" value="Master">
                    <label for="education4">Master</label><br>

                    <input id="education5" name="education" type="radio" value="Doctoral">
                    <label for="education5">Doctoral</label><br>

                    <input id="education6" name="education" type="radio" value="Not Available">
                    <label for="education6">None Of The Above</label><br>  

                    <label>Race:</label><br>
                    <input id="race1" name="race" type="checkbox" value="American Indian or Alaska Native">
                    <label for="race1">American Indian or Alaska Native</label><br>

                    <input id="race2" name="race" type="checkbox" value="Asian">
                    <label for="race2">Asian</label><br>

                    <input id="race3" name="race" type="checkbox" value="Black or African American">
                    <label for="race3">Black or African American</label><br>

                    <input id="race4" name="race" type="checkbox" value="Hispanic or Latino">
                    <label for="race4">Hispanic or Latino</label><br>

                    <input id="race5" name="race" type="checkbox" value="Native Hawaiian or Other Pacific Islander">
                    <label for="race5">Native Hawaiian or Other Pacific Islander</label><br>

                    <input id="race6" name="race" type="checkbox" value="White">
                    <label for="race6">White</label><br>

                    <input id="race7" name="race" type="checkbox" value="Other" onclick="toggleRaceOther(this)">
                    <label for="race7">Other</label><br>

                    <!-- Hidden input field for custom race -->
                    <div id="other-race-container" style="display: none;">
                        <label for="other-race-text">Please specify: </label>
                        <input id="other-race-text" name="other_race" type="text" maxlength="60">
                    </div>

                    <label>Gender:</label><br>
                    <input id="gender1" name="gender" type="radio" value="Male" required>
                    <label for="gender1">Male</label><br>

                    <input id="gender2" name="gender" type="radio" value="Female">
                    <label for="gender2">Female</label><br>

                    <input id="gender3" name="gender" type="radio" value="Non-binary">
                    <label for="gender3">Non-binary</label><br>

                    <input id="gender4" name="gender" type="radio" value="Other" onclick="toggleGenderOther(this)">
                    <label for="gender4">Other</label><br>

                    <!-- Hidden input field for custom gender -->
                    <div id="other-gender-container" style="display: none;">
                        <label for="other-gender-text">Please specify: </label>
                        <input id="other-gender-text" name="other_gender" type="text" maxlength="40">
                    </div>

                    <button id="submit-button" type="submit">Submit</button>
                </form>
            </div>

            <div id="warning">
                <p></p>
            </div>
        </div>

    <!-- JavaScript to handle showing/hiding other input fields -->
    <script>
        function toggleRaceOther(checkbox) {
            const otherRaceContainer = document.getElementById('other-race-container');
            otherRaceContainer.style.display = checkbox.checked ? 'block' : 'none';
        }

        function toggleGenderOther(checkbox) {
            const otherGenderContainer = document.getElementById('other-gender-container');
            otherGenderContainer.style.display = checkbox.checked ? 'block' : 'none';
        }
    </script>
    </body>
</html>
