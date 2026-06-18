<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

$table = $protect['database']['tables']['conversation'];

function responseFailure(int $code, string $message){
    http_response_code($code);
    $response['status'] = 'error';
    $response['message'] = $message;
    echo json_encode($response);
    exit;
}

if($_SERVER['REQUEST_METHOD'] == 'POST'){
    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        responseFailure(403, "Invalid CSRF Token");
    }

    $data = json_decode(file_get_contents('php://input'),true);

    if(
        !isset($data["likert_1"]) ||
        !isset($data["query_id"])
    ){
        responseFailure(400, "Missing required keys in body of POST request");
    }

    $likert_1 = $data["likert_1"];
    $likert_2 = isset($data["likert_2"]) ? $data["likert_2"] : null;
    $preference = isset($data["preference"]) ? (int)$data["preference"] : null;
    $query_id = $data['query_id'];

    $response = ['status' => 'success', 'database' => '', 'data' => ''];
    $response['data'] = ['likert_1' => $likert_1, 'likert_2' => $likert_2, 'preference' => $preference, 'query_id' => $query_id];

    $connection = new mysqli($host, $username, $password, $database);

    if($connection->connect_error){
        error_log("Connection Error". $connection->connect_error);
        responseFailure(500, "Database Connection Failed");
    } else {
        $stmt = $connection->prepare("UPDATE $table SET likert_1 = ?, likert_2 = ?, preference = ? WHERE query_id = ?");
        if(!$stmt){
            responseFailure(500, "Prepare Statement Failed");
        }

        if(!$stmt->bind_param(
            "iiii", 
            $likert_1,
            $likert_2,
            $preference,
            $query_id
            )){
            responseFailure(500, "bind_param statement failed");
        }

        if($stmt->execute()){
            $response['database'] = 'Database Insertion Successful';
        } else {
            responseFailure(500, "Execute Statement Failed");
        }

        $connection->close();
    }

    header('Content-Type: application/json');
    if($response['status'] == 'success'){
        http_response_code(200);
    } else {http_response_code(500);}
    echo json_encode($response);
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
