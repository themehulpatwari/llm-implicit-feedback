<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

header('Content-Type: application/json');

$table = $protect['database']['tables']['task'];

function responseFailure(int $code, string $message){
    http_response_code($code);
    $response['status'] = 'error';
    $response['message'] = $message;
    echo json_encode($response);
    exit;
}

if($_SERVER['REQUEST_METHOD'] == 'POST'){
    $response = ['status' => 'success', 'message' =>''];

    $data = json_decode(file_get_contents('php://input'), true);

    if(empty($data['task_id'])){
        responseFailure(400, "Missing keys in body of POST request");
    }

    $key = hex2bin($protect['encryption']['key']);
    $vector = hex2bin($protect['encryption']['vector']);

    $concatenatedString = strval($data['task_id']);
    $encryptedString = openssl_encrypt($concatenatedString, 'aes-256-cbc', $key, 0, $vector);

    $response['passcode'] = $encryptedString;

    http_response_code(200);
    echo json_encode($response);
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
