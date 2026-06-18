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
        <link rel="stylesheet" href="/public/css/sentence.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <script type="module" src="/public/js/events/sentence.js" defer></script>
    <script type='module' src='../js/functions/timeout.js' defer></script>

    <body>
        <?php
            $config = json_decode(file_get_contents('../../config/config.json'), true);
            include $config['path']['file']['webpage'] . 'header.php';
        ?>

        <form id="feedback-form" class="container">
            <div class="column">
                <label for="query">Past Question:</label>
                <div id="query" name="query" class="left-column" style="height: 10%; width: 75%;">Old Query</div>
                <label for="response">Past AI's Response:</label>
                <div id="response" name="response" class="left-column" style="height: 60%; width: 100%;">Left Column Element 2</div>
                <button style='height: 20px; width: 10%;' type="submit">Submit</button>
            </div>
            <div class="column"> 
                <label for="sentence"> From the AI’s response, please copy the sentence that you think best captures the main idea and paste it below.</label>
                <textarea id='sentence' name='sentence' type='text' placeholder='Copy & Paste' style="height: 10%;"></textarea>
                
                <label for="feedback"> (optional) If you have any other feedback, please respond below. </label>
                <textarea id='feedback' name='feedback' type='text' placeholder='Feedback' style="height: 20%;"></textarea>
            </div> 
        </form>
    </body>
</html>

<!--
use localstorage for query stuff. maybe use the stream algorithm for uniform chance o-o
-->