<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');

$response = ['status' => 'success', 'response' => ['task_id' => 0]];
function responseFailure(int $code, string $message){
    http_response_code($code);
    $response['status'] = 'error';
    $response['message'] = $message;
    echo json_encode($response);
    exit;
}

if($_SERVER['REQUEST_METHOD'] == 'GET'){
    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        http_response_code(403);
        exit('Invalid CSRF Token');
    }

    if(empty($_GET['next'])){
        responseFailure(400, "Missing keys in searchParams of GET request");
    }

    $param = trim($_GET['next']);
    $next = filter_var($param, FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
    if($next === null){
        responseFailure(400, 'Improper value for searchParam');
    }
    
    $index = $next ? $_SESSION['task_index'] + 1: $_SESSION['task_index'];
    $task_id = $_SESSION['task_array'][$index];

    if($task_id >= 0){
        $_SESSION['task_index'] = $index;
        $_SESSION['task_id'] = $task_id;   
    } else {
        $_SESSION['task_index'] = $index;
        $_SESSION['task_id'] = -1;    
    }

    header('Content-Type: application/json');
    $response['response']['calcd'] = $task_id;
    $response['response']['task_id'] = $_SESSION['task_id'];
    $response['response']['task_index'] = $_SESSION['task_index'];
    $response['response']['task_array'] = $_SESSION['task_array'];
    echo json_encode($response);
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
