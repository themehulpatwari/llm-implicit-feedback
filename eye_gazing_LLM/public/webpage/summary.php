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
        <link rel="stylesheet" href="/public/css/summary.css">
    </head>

    <script src="/public/js/events/summary.js" defer></script>
    <script type='module' src='../js/functions/timeout.js' defer></script>

    <body>
        <?php
            $config = json_decode(file_get_contents('../../config/config.json'), true);
            include $config['path']['file']['webpage'] . 'header.php';
        ?>

        <div style="display:flex; height: 98vh; align-items: center; justify-content: center;">
            <form id="summary-form">
                <label for="summary"> Please write a one or two sentence summary about what you learn from the conversation relating to the topic, <b>nothing about the AI please.</b></label>
                <textarea id='summary' name='summary' type='text' placeholder='Type your summary'></textarea>
                <button style='height: 20px; width: 10%;' type="submit">Submit</button>        
            </form>
        </div>
    </body>
</html>