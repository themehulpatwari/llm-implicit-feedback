<?php
session_start();

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');

header('Content-Type: application/json');

function responseFailure(int $code, string $message){
    http_response_code($code);
    echo json_encode([
        'status' => 'error',
        'message' => $message
    ]); 
    exit;
}

function responseSuccess(string $message){
    echo json_encode([
        'status' => 'success',
        'message' => $message
    ]);
    exit;
}

if($_SERVER['REQUEST_METHOD'] == 'GET'){
    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        responseFailure(403, "Invalid CSRF Token");
    }
    
    $_SESSION['conversation_1'] = [];
    $_SESSION['conversation_2'] = [];

    $_SESSION['selected_model_1'] = null;
    $_SESSION['selected_model_2'] = null;
    
    responseSuccess('Conversation was reset');
} else{
    responseFailure(405, "Method Not Allowed");
}
