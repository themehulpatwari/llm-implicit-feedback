<?php
session_start();

// Suppress warnings from vars.php which has session issues
$old_error_reporting = error_reporting(E_ERROR | E_PARSE);
include '../init/vars.php';
error_reporting($old_error_reporting);

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
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
    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        responseFailure(403, "Invalid CSRF Token");
    }

    $data = json_decode(file_get_contents('php://input'), true);

    if($data === null){
        responseFailure(400, "Invalid JSON in request body");
    }

    if(empty($data['task_id']) || !isset($data['accuracy'])){
        responseFailure(400, "Missing keys in body of POST request");
    }

    if(!isset($_SESSION["user_id"]) || empty($_SESSION["user_id"])){
        responseFailure(401, "User not authenticated - missing user_id in session");
    }

    $user_id = $_SESSION["user_id"];
    $task_id = (int) $data["task_id"];
    // $task_id = 100;
    $accuracy = (float) $data['accuracy'];
    if ($accuracy < 0){
        $accuracy = 0;
    }
    
    $response = ['status' => 'success', 'database' => '', 'user_id' => $user_id, 'task_id' => $task_id, 'accuracy' => $accuracy];

    $connection = new mysqli($host, $username, $password, $database);

    if($connection->connect_error){
        responseFailure(500, "Database Connection Failed");
    } else {
        $stmt = $connection->prepare("INSERT INTO $table (user_id, task_id, accuracy) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE accuracy = VALUES(accuracy)");
        if(!$stmt){
            responseFailure(500, "Prepare Statement Failed");
        }

        if(!$stmt->bind_param("sid", $user_id, $task_id, $accuracy)){
            responseFailure(500, "bind_param statement failed");
        }

        if($stmt->execute()){
            $response['database'] = 'Database Insertion Successful';
        } else {
            responseFailure(500, "Execute Statement Failed");
        }
        
        $connection->close();
    }

    if($response['status'] == 'success'){
        http_response_code(200);
    } else {
        http_response_code(500);
    }
    echo json_encode($response);
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
