<?php
session_start();
include '../init/vars.php';

// ini_set('display_errors', 1);
// error_reporting(E_ALL);

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
    $response = ['status' => 'success', 'database' => '', 'data' => ''];

    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        responseFailure(403, "Invalid CSRF Token");
    }

    $data = json_decode(file_get_contents('php://input'), true); 

    // if (
    //     empty($data['query']) ||
    //     empty($data['llm_response_1']) ||
    //     (empty($data['llm_response_2']) && $data['llm_response_2'] !== null) ||
    //     empty($data['llm_name_1']) ||
    //     (empty($data['llm_name_2']) && $data['llm_name_2'] !== null) ||
    //     empty($data['likert_1']) ||
    //     (empty($data['likert_2']) && $data['likert_2'] !== null) ||
    //     (empty($data['preference']) && $data['preference'] !== null) ||
    //     empty($data['timestamp'])
    // ) {
    //     responseFailure(400, "Missing keys in body of POST request");
    // }

    $user_id = $_SESSION['user_id'];
    $task_id = (int) $data["task_id"];
    // $user_id = "jcole";
    // $task_id = 1;

    $user_query = $data["query"];

    $llm_response_1 = $data["llm_response_1"];
    $llm_response_2 = $data["llm_response_2"];
    $llm_name_1 = $data["llm_name_1"];
    $llm_name_2 = $data["llm_name_2"];
    $adjustment = $data["adjustment"] ? 1 : 0;    
    $query_timestamp = $data["timestamp"];

    // $response['data'] = [
    //     'user_id' => $user_id, 
    //     "task_id" => $task_id, 
    //     "table" => $table,
    //     "user_query" => $user_query, 
    //     'llm_response_1' => $llm_response_1, 
    //     'llm_response_2' => $llm_response_2,
    //     'llm_name_1' => $llm_name_1,
    //     'llm_name_2' => $llm_name_2,
    //     'likert_1' => $likert_1,
    //     'likert_2' => $likert_2,
    //     'preference' => $preference,
    //     'query_timestamp' => $query_timestamp 
    // ];

    // $response['testing'] = gettype($task_id);
    
    $connection = new mysqli($host, $username, $password, $database);

    if($connection->connect_error){
        error_log("Connection Error". $connection->connect_error);
        responseFailure(500, "Database Connection Failed");
    } else {
        // $placeholders = implode(',', array_fill(0, 4, '?'));
        $stmt = $connection->prepare(
            "INSERT INTO query_logs_table 
            (user_id,task_id,user_query,llm_response_1,llm_response_2,llm_name_1,llm_name_2,adjustment,query_timestamp)
            VALUES (?,?,?,?,?,?,?,?,?)"
        );
//INSERT INTO `query_logs_table`(`user_id`, `task_id`, `user_query`, `llm_response_1`, `llm_response_2`, 
// `llm_name_1`, `llm_name_2`, `likert_1`, `likert_2`, `preference`, `adjustment`, `query_timestamp`) 
// VALUES ('[value-1]','[value-2]','[value-3]','[value-4]','[value-5]','[value-6]','[value-7]','[value-8]','[value-9]','[value-10]','[value-11]','[value-12]')

        $stmt->bind_param(
            "sisssssis", 
            $user_id, 
            $task_id, 
            $user_query, 
            $llm_response_1, 
            $llm_response_2, 
            $llm_name_1, 
            $llm_name_2, 
            $adjustment, 
            $query_timestamp
        );

        if($stmt->execute()){
            $query_id = $connection->insert_id;
            $response['query_id'] = $query_id;

            $response['database'] = 'Database Insertion Successful';
        } else {
            responseFailure(500, "Execute Statement Failed");
        }

        $connection->close();    
    }

    // echo '{user_id: ' . $user_id . ', query: ' . $query . ', llm: ' . $llm_response_1. ', task_id: ' . $task_id . ', time: ' . $time . '}';

    header('Content-Type: application/json');
    if($response['status'] == 'success'){
        http_response_code(200);
    } else {http_response_code(500);}
    echo json_encode($response);
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
