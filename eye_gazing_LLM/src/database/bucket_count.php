<?php
session_start();
// include_once '../init/vars.php';
function responseFailure(int $code, string $message){
    http_response_code($code);
    $response = ['status' => '', 'message' => ''];
    $response['status'] = 'error';
    $response['message'] = $message;
    echo json_encode($response);
    exit;
}
function get_model_buckets(array $models_list){
    global $host, $username, $password, $database;
    $connection = new mysqli($host, $username, $password, $database);
    
    $keys = $models_list;
    
    $buckets = array_fill_keys($keys, 0);
    
    if($connection->connect_error){
        error_log("Connection Error". $connection->connect_error);
        responseFailure(500, "Database Connection Failed");
    } else {
        $stmt = $connection->prepare("SELECT DISTINCT 
            t.user_id AS user_id, t.task_id AS task_id, q.llm_name_1 AS llm_name_1, q.llm_name_2 AS llm_name_2 
            FROM task_table AS t 
            INNER JOIN query_logs_table AS q 
                ON q.user_id = t.user_id AND q.task_id = t.task_id 
            WHERE t.understand_before IS NULL;
        ");

        if($stmt->execute()){
            $results = $stmt->get_result();
            
            while ($row = $results->fetch_assoc()) {
                foreach ($keys as $key){
                    foreach (['llm_name_1', 'llm_name_2'] as $col) {
                        if ($row[$col] === $key) {
                            $buckets[$key]++;
                        }
                    }
                }
            }
            
        } else {
            responseFailure(500, "Execute Statement Failed");
        }

        $connection->close();
    }

    return $buckets;
}
?>