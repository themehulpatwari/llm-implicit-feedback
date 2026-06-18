<?php
session_start();
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <link rel="stylesheet" href="/public/css/more.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <script type="module" src="/public/js/events/more.js" defer></script>
    <script type='module' src='../js/functions/timeout.js' defer></script>

    <body>
        <?php
            $config = json_decode(file_get_contents('../../config/config.json'), true);
            include $config['path']['file']['webpage'] . 'header.php';
        ?>

    <div class="likert-scale">
        <div class='convo'>
            <table>
                <tr>
                    <td></td>
                    <td>Very Little</td>
                    <td>Little</td>
                    <td>Somewhat</td>
                    <td>Much</td>
                    <td>Very Much</td>
                </tr>
                <tr>
                    <td>How much did you know the topic before the conversation?</td>
                    <td><input type="radio" name="understand-before" value="1" required></td>
                    <td><input type="radio" name="understand-before" value="2" required></td>
                    <td><input type="radio" name="understand-before" value="3" required></td>
                    <td><input type="radio" name="understand-before" value="4" required></td>
                    <td><input type="radio" name="understand-before" value="5" required></td>
                </tr>
                <tr>
                    <td>How much did you know the topic after the conversation?</td>
                    <td><input type="radio" name="understand-after" value="1" required></td>
                    <td><input type="radio" name="understand-after" value="2" required></td>
                    <td><input type="radio" name="understand-after" value="3" required></td>
                    <td><input type="radio" name="understand-after" value="4" required></td>
                    <td><input type="radio" name="understand-after" value="5" required></td>
                </tr>
            </table>
        </div>
    </div>

    <div style="display: flex; align-items: center; justify-content: center; width: 100vw;">
        <form id="finished" name="finished" action="pairwise.php" method="post" class="next-step-form">
            <button type="submit">Next Step</button>
        </form>
    </div>
    </body>
</html>

<!--
use localstorage for query stuff. maybe use the stream algorithm for uniform chance o-o
-->