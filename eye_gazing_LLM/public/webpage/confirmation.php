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
        <link rel="stylesheet" href="/public/css/general.css">
        <script type='module' src="/public/js/events/consent.js" defer></script>
        <script type='module' src='../js/functions/timeout.js' defer></script>
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <body>
        <div style="display:flex; justify-content: center;">
            <h2>Consent Form</h2>
        </div>

        <!-- CONSENT FORM -->
        <div id='consentID' style="text-align: center;">
            <div style="display: inline-block; text-align: left; border: 2px solid black; width: 66vw; height: 25vh; position: relative; vertical-align: middle; margin: 10px; padding: 2px;">
                This study requires the use of a web-camera, assumed to be connected to your device already for eye-tracking data collection. Additionally, mouse movement 
                will be recorded. These two methods are recorded to note the use of "user interaction" with the website. A video player will pop up for you to adjust yourself
                to stay inside a box but NO actual footage from your web-camera is EVER recorded for your privacy. The video player is only a tool for your physical position to 
                increase the accuracy of the eye-tracking software. The study is conducted by the [Anonymous Institution]. A questionnaire will ask for some basic 
                personal information (e.g: age, ethnicity). In the publication of this study, no personally identifiable information will ever be published and all data is 
                stored securely under the [Anonymous Institution].
            </div>
        </div>
        
        <!-- CONSENT CONFIRMATION INTERACTION -->
        <div>
            <form id='consentForm' name='consentForm' action='' method='post' style='text-align: center'>
                <p style='margin:2px'> By marking the checkbox and confirming, you agree to the consent form and will proceed with this study (including all future logins). </p>
                <input id='checkbox' name='checkbox' type='checkbox'></input>
                <button id='consentButton' type='submit'>Confirm</button>
            </form>
        </div>
        
        <!-- THANKS & PROCEEDING
        <div id='nextPageID' style='display:none'>
            <h1> 
                Thanks! There will be an instructions tab at the top if you need to refer to it again. You may proceed with the button below.
            </h1>
            <form id='thanks' name='thanks' action='/public/webpage/calibration.php' method='post' style='text-align: center'>
                <button id='proceedButton' type='submit'> Next Page </button>
            </form>
        </div> -->
    </body>
</html>


