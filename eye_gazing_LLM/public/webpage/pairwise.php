<?php
// Load config to set up session and authentication
include '../../src/init/config.php';

// Check if user is authenticated, redirect to login if not
// checkUserAuthentication();
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <link rel="stylesheet" href="/public/css/pairwise.css">
        <link rel="stylesheet" href="/public/css/eye.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <script type='module' src='/public/js/events/pairwise.js' defer></script>
    <script type="module" src="/public/js/events/task.js" defer></script>
    <script type='module' src='../js/functions/webgazer_init.js' defer></script>
    <script type='module' src='../js/functions/timeout.js' defer></script>
    <script type='module' src='../js/functions/stopwatch.js' defer></script>

    <script src="../../node_modules/WebGazer/dist/webgazer.js" defer></script>
    <script src='../../node_modules/heatmap.js/build/heatmap.js' type='text/javascript' defer></script>

    <body>
        <?php
            include 'header.php';
        ?>

        <div id='kdot' class='kdot' style='position:absolute; top: 0px; left: 0px; display: none'></div>

        <div>
            <p style="font-size: 18px; color: #e74c3c; font-weight: bold;">
                ⚠️ IMPORTANT: Please do not refresh this page during the task, as it will reset your progress.
            </p>
            <p style="font-size: 18px;">
                Please ask a minimum of three questions, though you're welcome and encouraged to ask additional questions if you'd like to explore further.
            </p>
            <p style="font-size: 18px;">
                Make sure to ask a question/query that is <u><b>open-ended/complex</b></u> and <u><b>not</b></u> answerable with "yes", "no", or simply stating a fact like an age number. Ask difficult questions such as "How did LeBron James' career impact the NBA?" rather than factual or easily verifiable questions such as "How tall is Lebron James?". After you type the question, please wait for a moment until the AI finishes generating their feedback.
            </p>
        </div>

        <div id="task-specific">
            <p></p>
        </div>
        
        <form id='searchForm' name='searchForm' action='pairwise.php' method='post' class='search-form'>
            <input name='query' type='text' placeholder='Type a question'></input>
            <button type='submit'>Enter</button>
        </form>

        <div id="column-container" class="column-container">
            <div id='column-1'>
                <div class='response-container'>
                    <p id='llm-response-1'>After you type your question, please wait patiently. It might take up to 1 minute for AI to finish generating their answer. The AI's response will show up here.</p>
                </div>
            </div>

            <div id='column-2'>
                <div class='response-container'>
                    <p id='llm-response-2'>After you type your question, please wait patiently. It might take up to 1 minute for AI to finish generating their answer. The AI's response will show up here.</p>
                </div>
            </div>
        </div>

        <div style='height: 100px;'></div>

        <div id= "questions-text" style="display:flex; align-items: center; justify-content: center; width: 98vw; visibility: hidden;">
            <h2>Questions Below</h2>
        </div>

        <div style="height: 36px;"></div>

        <div id="likert-scale-id" class="likert-scale" style="visibility: hidden;">
            <table>
                <tr>
                    <td></td>
                    <td>Very Dissatisfied</td>
                    <td>Dissatisfied</td>
                    <td>Neutral</td>
                    <td>Satisfied</td>
                    <td>Very Satisfied</td>
                </tr>
                <tr>
                    <td>Left Response</td>
                    <td><input type="radio" name="response1-likert" value="1" required></td>
                    <td><input type="radio" name="response1-likert" value="2" required></td>
                    <td><input type="radio" name="response1-likert" value="3" required></td>
                    <td><input type="radio" name="response1-likert" value="4" required></td>
                    <td><input type="radio" name="response1-likert" value="5" required></td>
                </tr>
                <tr>
                    <td>Right Response</td>
                    <td><input type="radio" name="response2-likert" value="1" required></td>
                    <td><input type="radio" name="response2-likert" value="2" required></td>
                    <td><input type="radio" name="response2-likert" value="3" required></td>
                    <td><input type="radio" name="response2-likert" value="4" required></td>
                    <td><input type="radio" name="response2-likert" value="5" required></td>
                </tr>
            </table>
            <table>
                <tr>
                    <td></td>
                    <td>Left Response</td>
                    <td>Right Response</td>
                </tr>
                <tr>
                    <td>Which response did you like better?</td>
                    <td><input type="radio" name="preferred-response" value="1" required></td>
                    <td><input type="radio" name="preferred-response" value="2" required></td>
                </tr>
            </table>
        </div>

        <div style="height:20px;" ></div>

        <div id="scroll-instruction" class="scroll-instruction">
            After you answer all the questions, please scroll up to ask the next question.
        </div>

        <div style="display: flex; align-items: center; justify-content: center; width: 100vw;">
            <form id="finished" name="finished" action="pairwise.php" method="post" class="next-step-form" style="visibility: hidden;">
                <button type="submit">Next Step</button>
            </form>
        </div>

        <script type="module">
            import { startStopwatch } from '../js/functions/stopwatch.js';
            document.addEventListener('DOMContentLoaded', () => {
                startStopwatch();
            });
        </script>

        <div style='height:30px;'></div>
    </body>
</html>