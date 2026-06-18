<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <link rel="stylesheet" href="/public/css/passcode.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <script type="module" src="/public/js/events/passcode.js" defer></script>

    <body>
        <div>
            <h2>Thank you very much for participating</h2>
            <p class="passcode">PASSCODE</p>
            <p class="encrypted" id="passcode"></p>
            <p class="instructions">You can copy and paste this passcode to the MTurk task to receive your reward.</p>
            <form id="finished" name="finished" method="post" class="search-form">
                <button type="submit">Finished</button>
            </form>
        </div>
    </body>
</html>
