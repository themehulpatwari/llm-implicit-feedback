<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

header('Content-Type: application/json');

$record_table = $protect['database']['tables']['record'];
$task_table = $protect['database']['tables']['task'];

function responseFailure(int $code, string $message){
    http_response_code($code);
    $response['status'] = 'error';
    $response['message'] = $message;
    echo json_encode($response);
    exit;
}

if($_SERVER['REQUEST_METHOD'] == 'POST'){
    $response = ['status' => 'success', 'message' =>'', 'data' => []];

    $data = json_decode(file_get_contents('php://input'), true);

    if(empty($data['user_id']) || empty($data['tasks'])){
        responseFailure(400, "Missing keys in body of POST request");
    }

    // $user_id = filter_var($data['user_id'], FILTER_SANITIZE_NUMBER_INT);
    // $user_id = filter_var($user_id, FILTER_VALIDATE_INT);
    // if ($user_id === false) {
    //     responseFailure(400, "Non-Integer ID");
    // }
    $user_id = $data['user_id'];

    $tasks_string_array = $data["tasks"];
    // $response['tasks'] = $data['tasks'];
    $task_ids = array_map(function($t) { return intval($t['value']); }, $tasks_string_array); 
    $tasks = $task_ids; // Use the correctly extracted task IDs
    $selected_labels = array_map(function($t) { return $t['label']; }, $tasks_string_array);
    $domain_value = implode(", ", $selected_labels);
    $response['domain_value'] = $domain_value;
    $response['task_ids'] = $task_ids;

    $connection = new mysqli($host, $username, $password, $database);

    if($connection->connect_error){
        error_log("Connection Error". $connection->connect_error);
        responseFailure(500, "Database Connection Failed");
    }

    $stmt = $connection->prepare("SELECT COUNT(*) as count from $record_table WHERE user_id = ?");
    // if(!$stmt){
    //     responseFailure(500, "Prepare Statement Failed");
    // }

    $stmt->bind_param("s", $user_id);

    if($stmt->execute()){
        $row = $stmt->get_result()->fetch_assoc();
        $not_in_table = $row['count'] === 0;
        // $response['message'] = $row['count'] . " " . $user_id;
        // echo json_encode($response);
        $response['not_in_table'] = $not_in_table;

        if($not_in_table){
            $stmt = $connection->prepare("INSERT INTO $record_table (user_id) VALUES (?)");
            if(!$stmt){
                responseFailure(500, "Prepare Statement Failed");
            }

            $stmt->bind_param("s", $user_id);
            if(!$stmt->execute()){
                responseFailure(500, "Execute Statement Failed");
            }
            
            $_SESSION['user_id'] = $user_id;
            $_SESSION['task_array'] = $tasks;
            $_SESSION['task_index'] = 0;
            $_SESSION['task_id'] = $tasks[0];
            $response['message'] = 'User ID saved to session and database';

            for ($i = 0; $i < count($tasks); $i++) {
                $task_id = $tasks[$i];
                $label = $selected_labels[$i]; 
            
                $stmt = $connection->prepare("INSERT INTO $task_table (user_id, task_id, domain) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE domain = VALUES(domain)");
                if(!$stmt){
                    responseFailure(500, "Prepare Statement Failed (task_table insert/update)");
                }
                $stmt->bind_param("sis", $user_id, $task_id, $label);
                if(!$stmt->execute()){
                    responseFailure(500, "Execute Statement Failed (task_table insert/update)");
                }
            }
        } else {
            $placeholders = implode(',', array_fill(0, count($tasks), '?'));
            $response['placeholders'] = $placeholders;
            $stmt = $connection->prepare("SELECT task_id as tasks from $task_table WHERE task_id in ($placeholders) AND user_id = ? and finished is not null");
            // if(!$stmt){
            //     responseFailure(500, "Prepare Statement Failed");
            // }

            $merged = array_merge($tasks, [$user_id]);
            $stmt->bind_param( str_repeat('i', count($tasks)) . 's', ...$merged); 
            if($stmt->execute()){
                $result = $stmt->get_result();
                $response['result'] = $result;

                if($result->num_rows > 0){
                    $tasks_done = [];
                    while ($row = $result->fetch_assoc()) {
                        $tasks_done[] = $row['tasks'];
                    }

                    $response['status'] = 'failure';
                    $response['data'] = $tasks_done;
                    $response['message'] = "User ID $user_id has already done some of these tasks";
                } else {
                    $stmt = $connection->prepare("SELECT age from $record_table where user_id = ?");

                    $stmt->bind_param("s", $user_id);
                    $stmt->execute();

                    $result = $stmt->get_result();
                    $row = $result->fetch_assoc();
                    // $response['message'] = is_null($row['age']);
                    if (!is_null($row['age'])) {
                        $response['message'] = "User has filled out questionnaire"; // calibration
                    } else {
                        $response['message'] = "User has not finished the questionnaire";
                    }

                    $_SESSION['task_array'] = $tasks;
                    $_SESSION['task_index'] = 0;
                    $_SESSION['task_id'] = $tasks[0];

                    $_SESSION['user_id'] = $user_id;
                    // $response['data'] = [
                    //     "task_array" => $tasks, 
                    //     "task_index" => 0, 
                    //     "task_id" => $tasks[0], 
                    //     'session_user_id' => $_SESSION['user_id'], 
                    //     'session_task_id' =>$_SESSION['task_id'],
                    //     'session_task_id_type' => gettype($_SESSION['task_id'][0]),
                    // ];

                    // Always insert/update domain for all tasks in the request
                    for ($i = 0; $i < count($tasks); $i++) {
                        $task_id = $tasks[$i];
                        $label = $selected_labels[$i]; 
                        
                        $stmt = $connection->prepare("INSERT INTO $task_table (user_id, task_id, domain) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE domain = VALUES(domain)");
                        if(!$stmt){
                            responseFailure(500, "Prepare Statement Failed (task_table insert/update)");
                        }
                        $stmt->bind_param("sis", $user_id, $task_id, $label);
                        if(!$stmt->execute()){
                            responseFailure(500, "Execute Statement Failed (task_table insert/update)");
                        }
                    }
                }
            } else{
                responseFailure(500, "Execute Statement Failed");
            }
        }
    } else {
        error_log("Error: " . $stmt->error);
        responseFailure(500,"Execute Statement Failed");
    }

    $connection->close();
    
    http_response_code(200);
    echo json_encode($response);
} else {
    responseFailure(405, "Method Not Allowed");
}
?>