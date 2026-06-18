<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

$table = $protect['database']['tables']['record'];

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

    if(empty($data['age']) || empty($data['location']) || empty($data['education']) || empty($data['race']) || empty($data['gender'])){
        responseFailure(400, "Missing keys in body of POST request");
    }

    $age = (int) filter_var($data['age'], FILTER_SANITIZE_NUMBER_INT); 
    $location = $data['location'];
    $education = $data['education'];
    $race = implode(',', $data['race']);
    $gender = $data['gender'];

    $response = ['status' => 'success', 'database' => '', 'data' => ''];
    $user_id = $_SESSION['user_id'];
    // $response['data'] = ['type_age' => gettype($age),'age' => $age, 'location' => $location, 'education'=> $education,'race' => $race, 'gender' => $gender,'user_id'=> $user_id];

    $connection = new mysqli($host, $username, $password, $database);

    if($connection->connect_error){
        error_log("Connection Error". $connection->connect_error);
        responseFailure(500, "Database Connection Failed");
    } else {
        $stmt = $connection->prepare("UPDATE $table SET age = ?, location = ?, education = ?, race = ?, gender = ? WHERE user_id = ?;");
        if(!$stmt){
            responseFailure(500, "Prepare Statement Failed");
        }

        if(!$stmt->bind_param("isssss", $age, $location, $education, $race, $gender, $user_id)){
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

//Copy and paste but only take one input for this request. This means lines 29-33 are compressed to a single line, line 45 only sets ACCURACY = ?, and line 50 is a bind_param of "is" with $accuracy, $user_id.
//You need to add the column to the database for this table. This column is defaulted null