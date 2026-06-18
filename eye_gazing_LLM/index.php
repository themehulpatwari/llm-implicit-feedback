<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title></title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    
    <?php
        $config = json_decode(file_get_contents('/path/to/secure/config.json'), true);
        $protect = json_decode(file_get_contents('/path/to/secure/protected.json'), true);
        
        
        $MAX_TASKS = 45;
        // Include the task_count file
        require_once './src/database/task_count.php';
        
        // Get task count using the new function
        $task_count = getTaskCount();
        // Check if the task count exceeds the maximum allowed
        if ($task_count > $MAX_TASKS) {
            header('Location: ' . $config['path']['web']['webpage'] . 'finished_batch.php');
        } else {
            header('Location: ' . $config['path']['web']['webpage'] . 'login.php');
        }
    ?>
<div>
    This task is closed for now. Thanks for participating!
</div>
</html>

<!-- @inproceedings{papoutsaki2016webgazer,
  author = {Alexandra Papoutsaki and Patsorn Sangkloy and James Laskey and Nediyana Daskalova and Jeff Huang and James Hays},
  title = {WebGazer: Scalable Webcam Eye Tracking Using User Interactions},
  booktitle = {Proceedings of the 25th International Joint Conference on Artificial Intelligence (IJCAI)},
  pages = {3839--3845},
  year = {2016},
  organization={AAAI}
} -->