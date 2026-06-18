<?php
session_start();
include '../init/vars.php';
/**
 * task_count.php
 * 
 * Returns the count of finished tasks from the task table
 */

$task_table = $protect['database']['tables']['task'];
// Include necessary configuration files
// require_once __DIR__ . '/../../config/config.json';
// require_once __DIR__ . '/../../config/protected.json';

/**
 * Gets the count of finished tasks from the database
 * 
 * @return int The count of finished tasks
 */
function getTaskCount() {
    global $host, $username, $password, $database, $task_table;

    // Initialize task count
    $task_count = 0;
    
    try {
        $connection = new mysqli($host, $username, $password, $database);
        
        if ($connection->connect_error) {
            error_log("Connection Error: " . $connection->connect_error);
            return $task_count;
        }
        
        // Get total count of rows in task_table where finished is not NULL
        $sql = "SELECT COUNT(*) as total FROM $task_table WHERE finished is not NULL";
        $result = $connection->query($sql);
        
        if ($result && $row = $result->fetch_assoc()) {
            $task_count = (int)$row['total'];
        } else {
            error_log("Query Error: " . $connection->error);
        }

        $connection->close();
    } catch (Exception $e) {
        error_log("Error counting task rows: " . $e->getMessage());
    }
    
    return $task_count;
}

// If this file is called directly, return the count as JSON
if (basename($_SERVER['PHP_SELF']) == basename(__FILE__)) {
    // Set proper JSON content type header
    header('Content-Type: application/json');
    // Make sure nothing else is output before the JSON
    if (ob_get_length()) ob_clean();
    // Return a properly formatted JSON response
    echo json_encode(['task_count' => getTaskCount()]);
    exit; // Terminate execution to prevent additional output
}
?>