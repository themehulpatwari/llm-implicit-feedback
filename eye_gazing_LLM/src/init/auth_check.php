<?php
/**
 * Authentication check function
 * Checks if user is logged in (has valid session with user_id)
 * If not logged in, shows notification and redirects to login page
 */

function checkUserAuthentication($redirect_to_login = true) {
    // Ensure session is started
    if (session_status() == PHP_SESSION_NONE) {
        session_start();
    }
    
    // Check if user_id exists and has a valid value (not empty, not "none")
    $is_authenticated = isset($_SESSION['user_id']) && 
                       !empty($_SESSION['user_id']) && 
                       $_SESSION['user_id'] !== "none";
    
    if (!$is_authenticated && $redirect_to_login) {
        // Clear the session data
        session_destroy();
        
        // Show notification message and redirect to login
        echo '<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Session Expired</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .notification-container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }
        .error-icon {
            font-size: 48px;
            color: #e74c3c;
            margin-bottom: 20px;
        }
        .error-title {
            font-size: 24px;
            color: #333;
            margin-bottom: 15px;
        }
        .error-message {
            font-size: 16px;
            color: #666;
            margin-bottom: 25px;
            line-height: 1.5;
        }
        .redirect-info {
            font-size: 14px;
            color: #999;
            margin-bottom: 20px;
        }
        .login-button {
            background-color: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .login-button:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="notification-container">
        <div class="error-icon">⚠️</div>
        <div class="error-title">Session Expired</div>
        <div class="error-message">
            Your session has expired or you are not logged in. Please log in again to continue using the eye-gazing task system.
        </div>
        <div class="redirect-info">
            You will be redirected to the login page automatically in 3 seconds...
        </div>
        <a href="/public/webpage/login.php" class="login-button">Go to Login Page</a>
    </div>
    
    <script>
        // Redirect after 3 seconds
        setTimeout(function() {
            window.location.href = "/public/webpage/login.php";
        }, 3000);
    </script>
</body>
</html>';
        exit();
    }
    
    return $is_authenticated;
}

/**
 * Check authentication without redirect (for AJAX endpoints)
 */
function checkUserAuthenticationAjax() {
    return checkUserAuthentication(false);
}
?>
