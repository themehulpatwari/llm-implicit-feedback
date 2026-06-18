<?php
session_start();
include '../init/vars.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

$table = $protect['database']['tables']['behavior'];

//MAKE SURE THIS SCRIPT HAS ACCESS TO WRITE TO THE DESIRED DIRECTORY
header("Content-Type: application/json");

$response = ['status' => 'success', 'message' => ''];
function responseFailure(int $code, string $message){
    global $response;
    http_response_code($code);
    $response['status'] = 'error';
    $response['message'] = $message;
    echo json_encode($response);
    exit;
}

// function responseSuccess(string $message){
//     global $response;
//     $response['message'] = $message;
//     echo json_encode($response);
//     exit;
// }

if($_SERVER['REQUEST_METHOD'] == 'POST'){
    if($_SERVER['HTTP_X_CSRF_TOKEN'] != $_SESSION['csrf_token']){
        responseFailure(403, 'Invalid CSRF Token');
    }
    
    $data = json_decode(file_get_contents('php://input'), true);

    if(
        empty($data['absolute_gaze_data']) || 
        empty($data['absolute_mouse_data']) || 
        empty($data['relative_mouse_data_left']) ||
        empty($data['relative_mouse_data_right']) || 
        empty($data['relative_gaze_data_left']) || 
        empty($data['relative_gaze_data_right']) ||
        empty($data['task_id'])
    ){
        responseFailure(400, "Missing keys in POST request");
    }

    $absolute_mouse_data = $data['absolute_mouse_data'];
    $absolute_gaze_data = $data['absolute_gaze_data'];

    $relative_mouse_data_left = $data['relative_mouse_data_left'];
    $relative_mouse_data_right = $data['relative_mouse_data_right'];
    $relative_gaze_data_left = $data['relative_gaze_data_left'];
    $relative_gaze_data_right = $data['relative_gaze_data_right'];

    $user_id = $_SESSION['user_id'];
    $task_id = $data['task_id'];
    
    $user_task_dir = $base_data_pathname . $user_id . '/' . $task_id . '/';
    
    // if(!$_SESSION['write_to_file']){
    //     responseSuccess('"Writing to files" was turned off');
    // }

    $absolute_mouse_pathname = $user_task_dir .'abs_mouse.csv';
    $absolute_gaze_pathname = $user_task_dir . 'abs_gaze.csv';

    $relative_mouse_pathname_left = $user_task_dir .'rel_mouse_left.csv';
    $relative_mouse_pathname_right = $user_task_dir .'rel_mouse_right.csv';
    $relative_gaze_pathname_left = $user_task_dir . 'rel_gaze_one.csv';
    $relative_gaze_pathname_right = $user_task_dir . 'rel_gaze_two.csv';

    // $response['message'] = ['type' => gettype($task_id), 'amp' => $absolute_mouse_pathname, 'agp' => $absolute_gaze_pathname, 'rmpl' => $relative_mouse_pathname_left,
    // 'rmpr' => $relative_mouse_pathname_right, 'rgpl' => $relative_gaze_pathname_left, 'rgpr' => $relative_gaze_pathname_right], 
    // 'amd' => $absolute_mouse_data, 'agd' => $absolute_gaze_data,
    // 'rmdl' => $relative_mouse_data_left, 'rmdr' => $relative_mouse_data_right, 'rgdl' => $relative_gaze_data_left, 'rgdr' => $relative_gaze_data_right];

    if(!is_null($task_id) && !file_exists($user_task_dir)){
        mkdir($user_task_dir, 0775, true);
        
        $connection = new mysqli($host, $username, $password, $database);

        if($connection->connect_error){
            error_log("Connection Error". $connection->connect_error);
            responseFailure(500, "Database Connection Failed");
        } else {
            $stmt = $connection->prepare("INSERT INTO $table
                (
                    user_id, 
                    task_id, 
                    absolute_mouse_pathname, 
                    relative_mouse_pathname_left, 
                    relative_mouse_pathname_right, 
                    absolute_gaze_pathname, 
                    relative_gaze_pathname_left, 
                    relative_gaze_pathname_right
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)");

            $stmt->bind_param(
                "sissssss", 
                $user_id, 
                $task_id, 
                $absolute_mouse_pathname, 
                $relative_mouse_pathname_left, 
                $relative_mouse_pathname_right, 
                $absolute_gaze_pathname, 
                $relative_gaze_pathname_left, 
                $relative_gaze_pathname_right
            );

            if(!$stmt->execute()){
                error_log("Error: " . $stmt->error);
                responseFailure(500, 'Execute Statement Failed');
            }

            $connection->close();
        }
    }

    $file_error = false;

    $file = fopen($absolute_gaze_pathname, 'a');
    if($file){
        foreach ($absolute_gaze_data as $instance) {
            $string = implode(',', (array) $instance) . "\n";
            fwrite($file, $string);
        }
        fclose($file);
    } else {
        $file_error = true;
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
    if (!writeToCsv($relative_gaze_pathname_left, $relative_gaze_data_left)) {
        $file_error = true;
    }
    if (!writeToCsv($relative_gaze_pathname_right, $relative_gaze_data_right)) {
        $file_error = true;
    }
    if (!writeToCsv($absolute_mouse_pathname, $absolute_mouse_data)) {
        $file_error = true;
    }
    if (!writeToCsv($relative_mouse_pathname_left, $relative_mouse_data_left)) {
        $file_error = true;
    }
    if (!writeToCsv($relative_mouse_pathname_right, $relative_mouse_data_right)) {
        $file_error = true;
    }

    if($file_error){
        responseFailure(500, 'File Saving Failed');
    }
    
    echo json_encode($response);
    exit;
} else {
    http_response_code(405);
    echo 'Method Not Allowed';
}
