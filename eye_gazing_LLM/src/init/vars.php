<?php
session_start();
$data = '/path/to/secure/protected.json';

$protect = json_decode(file_get_contents($data), true);
$host = $protect['database']['host'];
$username = $protect['database']['user'];
$password = $protect['database']['password'];
$database = $protect['database']['database'];

$base_data_pathname = "/path/to/secure/user_behavior/";

$ip = $_SERVER['REMOTE_ADDR'];
$now = time();

$last_request = $_SESSION['rate_limit'][$ip]['last_request'];
$request_count = $_SESSION['rate_limit'][$ip]['request_count'];

//Reject if >100 requests in 60 seconds
if ($now - $last_request > 60) {
    $_SESSION['rate_limit'][$ip] = ['last_request' => $now, 'request_count' => 1];
} else {
    if ($request_count > 100) {
        header('HTTP/1.1 429 Too Many Requests');
        echo 'Rate limit exceeded';
        // exit;
    } else {
        $_SESSION['rate_limit'][$ip]['request_count']++;
    }
}
