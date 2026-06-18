<?php
session_set_cookie_params([
    'secure' => true,     // Send cookie only over HTTPS
    'httponly' => true,   // Prevent JavaScript access
    'samesite' => 'Lax'   // Control cross-site cookie sharing
]);

session_start();
session_regenerate_id(true);

// Include authentication check functions
include_once __DIR__ . '/auth_check.php';

if(empty($_SESSION['csrf_token'])){
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}

if(empty($_SESSION['write_to_file'])){
    $_SESSION['write_to_file'] = true;
}

// Don't set user_id to "none" by default - let it remain unset until login
// This allows the auth check to work properly

if(empty($_SESSION['task_id'])){
    $_SESSION['task_id'] = -1;
}   

if(empty($_SESSION['task_array'])){
    $_SESSION['task_array'] = [];
}

if(empty($_SESSION['task_index'])){
    $_SESSION['task_index'] = (int)0;
}

if(empty($_SESSION['conversation_1'])){
    $_SESSION['conversation_1'] = [];
}

if(empty($_SESSION['conversation_2'])){
    $_SESSION['conversation_2'] = [];
}

if(empty($_SESSION['selected_model_1'])){
    $_SESSION['selected_model_1'] = null;
}

if(empty($_SESSION['selected_model_2'])){
    $_SESSION['selected_model_2'] = null;
}

// Initialize rate limiting if needed (fix undefined variables)
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$now = time();
if (!isset($_SESSION['rate_limit'][$ip])) {
    $_SESSION['rate_limit'][$ip] = ['last_request' => $now, 'request_count' => 1];
}