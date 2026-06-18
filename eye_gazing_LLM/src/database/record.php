<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');

$table = $protect['database']['tables']['record'];

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

    if(empty($_GET['checkbox'])){
        responseFailure(400, "Missing keys in GET request");
    }
    $consent = htmlspecialchars($_GET['checkbox']);
    $consent = $consent === 'on' ? 1 : 0;

    $response = ['status' => 'success', 'database' => '', 'data' => ''];

    $user_id = $_SESSION['user_id'];

    $connection = new mysqli($host, $username, $password, $database);
    if($connection -> connect_error){
        error_log("Connection Error". $connection->connect_error);
        responseFailure(500, "Database Connection Failed");
    }
    
    $stmt = $connection->prepare("UPDATE $table SET consent = ? WHERE user_id = ?");
    if(!$stmt){
        responseFailure(500, "Prepare Statement Failed");
    }

    $stmt->bind_param("is", $consent, $user_id, );

    if($stmt->execute()){
        $response['database'] = 'Database Insertion Successful';
    } else {
        responseFailure(500, "Execute Statement Failed");
    }

    $connection->close();

    header('Content-Type: application/json');
    if($response['status'] == 'success'){
        http_response_code(200);
    } else {http_response_code(500);}
    echo json_encode($response);
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
