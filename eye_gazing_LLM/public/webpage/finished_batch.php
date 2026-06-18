<?php
$config = json_decode(file_get_contents('../../config/config.json'), true);
include $config['path']['file']['init'] . 'config.php';

// Clear all existing session data for fresh login
session_unset();
session_destroy();

// Start a new session
session_start();
session_regenerate_id(true);

// Initialize fresh CSRF token
if(empty($_SESSION['csrf_token'])){
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="description" content="Batch completion notification">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <link rel="stylesheet" href="/public/css/finished_batch.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <body>
        <div class="container"> 
            <div>
                <h1>Batch Complete</h1>
                <div class="instructions">
                    <p>We have finished collecting this batch of data.</p>
                    <p>The next batch will be released soon.</p>
                    <p>Thank you for your interest in our study!</p>
                </div>

                <div class="info-section">
                    <h2>What's Next?</h2>
                    <p>We regularly release new batches of tasks. Please check back later for new opportunities to participate.</p>
                    <p>If you have already completed tasks and have questions about your payment, please contact us.</p>
                </div>

                <footer>
                    For any additional help/inquiries: the study administrator
                </footer>
            </div>
        </div>
    </body>
</html>


