<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

$table = $protect['database']['tables']['behavior'];

//MAKE SURE THIS SCRIPT HAS ACCESS TO WRITE TO THE DESIRED DIRECTORY

if($_SERVER['REQUEST_METHOD'] == 'POST'){
    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        http_response_code(403);
        exit('Invalid CSRF Token');
    }
    $response = ['status' => 'success', 'database' =>'', 'file-saving' => ''];

    $data = json_decode(file_get_contents('php://input'), true);

    if(
        empty($data['absolute_gaze_data']) || 
        empty($data['relative_gaze_data']) || 
        empty($data['absolute_mouse_data']) || 
        empty($data['relative_mouse_data']) ||
        empty($data['task_id'])
    ){
        http_response_code(400);
        echo 'Missing keys in body of POST request';
        exit;
    }

    $absolute_gaze_data = $data['absolute_gaze_data'];
    $relative_gaze_data = $data['relative_gaze_data'];
    $absolute_mouse_data = $data['absolute_mouse_data'];
    $relative_mouse_data = $data['relative_mouse_data'];
    
    $user_id = $_SESSION['user_id'];
    $task_id = (int) $data['task_id'];
    
    $user_task_dir = $base_data_pathname . $user_id . '/' . $task_id . '/';
    
    // if(!$_SESSION['write_to_file']){
    //     echo json_encode($response);
    //     exit;
    // }
    
    $absolute_gaze_pathname = $user_task_dir . 'abs_gaze.csv';
    $relative_gaze_pathname = $user_task_dir . 'rel_gaze.csv';
    $absolute_mouse_pathname = $user_task_dir .'abs_mouse.csv';
    $relative_mouse_pathname = $user_task_dir .'rel_mouse.csv';

    if(!is_null($task_id) && !file_exists($user_task_dir)){
        mkdir($user_task_dir,0775, true);
        
        $connection = new mysqli($host, $username, $password, $database);

        if($connection->connect_error){
            error_log("Connection Error". $connection->connect_error);
            http_response_code(500);
            $response['status'] = "error";
            $response["database"] = "Database Connection Failed";
        } else {
            $stmt = $connection->prepare("INSERT INTO $table 
                (user_id, task_id, absolute_mouse_pathname, relative_mouse_pathname_left, absolute_gaze_pathname, relative_gaze_pathname_left) 
                VALUES (?, ?, ?, ?, ?, ?)");
            if(!$stmt){
                http_response_code(500);
                $response['status'] = 'error';
                $response['database'] = 'Prepare Statement Failed';
            }

            $stmt->bind_param(
                "sissss", 
                $user_id, $task_id, $absolute_mouse_pathname, $relative_mouse_pathname, $absolute_gaze_pathname, $relative_gaze_pathname
            );

            if($stmt->execute()){
                $response['database'] = 'Database Insertion Successful';
            } else {
                error_log("Error: " . $stmt->error);
                http_response_code(500);
                $response['status'] = 'error';
                $response['database'] = 'Execute Statement Failed';
            }

            $connection->close();
        }
    }

    function writeToCsv($filePath, $data) {
        $file = fopen($filePath, 'a');
        if ($file) {
            // foreach ($data as $instance) {
            //     $instanceArray = (array) $instance;
            //     fputcsv($file, $instanceArray); 
            // }
            // fclose($file);
            foreach ($data as $instance) {
                $string = implode(',', (array) $instance) . "\n";
                fwrite($file, $string);
            }
            fclose($file);
        } else {
            return false; 
        }
        return true;
    }
    
    //could do this better
    $file_error = false;
    
    if (!writeToCsv($absolute_gaze_pathname, $absolute_gaze_data)) {
        $file_error = true;
    }    
    if (!writeToCsv($relative_gaze_pathname, $relative_gaze_data)) {
        $file_error = true;
    }
    if (!writeToCsv($absolute_mouse_pathname, $absolute_mouse_data)) {
        $file_error = true;
    }  
    if (!writeToCsv($relative_mouse_pathname, $relative_mouse_data)) {
        $file_error = true;
    }

    if($file_error){
        http_response_code(500);
        $response['status'] = 'error';
        $response['file_saving'] = 'File saving failed';
    }
    
    header("Content-Type: application/json");
    echo json_encode($response);
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
