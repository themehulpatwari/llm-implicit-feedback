<?php
// Load config to set up session and authentication
include '../../src/init/config.php';

// Check if user is authenticated, redirect to login if not
checkUserAuthentication();
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <!-- <link rel='stylesheet' href="/public/css/page1.css"> -->
        <link rel="stylesheet" href="/public/css/pointwise.css">
        <link rel="stylesheet" href="/public/css/eye.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <script type='module' src='/public/js/events/pointwise.js' defer></script>
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
        
        <!-- Comparison section, hidden by default, shown after the first question -->
        

        <form id='searchForm' name='searchForm' action='pointwise.php' method='post' class='search-form'>
            <input name='query' type='text' placeholder='Type a question' ></input>
            <button type='submit'>Enter</button>
        </form>

        <div id='response-1' class='response-container'>
            <p id='llm-response-1'>After you type your question, please wait patiently. It might take up to 1 minute for AI to finish generating their answer. The AI's response will show up here.</p>
        </div>

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
                    <td>Response</td>
                    <td><input type="radio" name="response1-likert" value="1" required></td>
                    <td><input type="radio" name="response1-likert" value="2" required></td>
                    <td><input type="radio" name="response1-likert" value="3" required></td>
                    <td><input type="radio" name="response1-likert" value="4" required></td>
                    <td><input type="radio" name="response1-likert" value="5" required></td>
                </tr>
            </table>
        </div>

        <div id="comparison-section" class="comparison-section" style="display: none;">
            <div class="comparison-header">
                <h3>Compare AI Responses</h3>
                <p>Please review both answers and provide your feedback on their relative quality.</p>
            </div>
            
            <div class="answers-comparison">
                <div class="answer-card">
                    <div class="answer-label">Previous Answer</div>
                    <div id="previous-answer" class="answer-content"></div>
                </div>
                
                <div class="answer-card">
                    <div class="answer-label">Current Answer</div>
                    <div id="current-answer" class="answer-content"></div>
                </div>
            </div>
            
            <div class="feedback-section">
                <label class="feedback-label">How does the current answer compare to the previous one?</label>
                <select id="comparison-feedback" class="feedback-select">
                    <option value="">Select your assessment...</option>
                    <option value="1">Current answer is better</option>
                    <option value="0">Current answer is worse</option>
                </select>
            </div>
        </div>

        <div id="scroll-instruction" class="scroll-instruction">
            After you answer all the questions, please scroll up to ask the next question.
        </div>

        <form id="finished" name="finished" action="pointwise.php" method="post" class="next-step-form" style="visibility: hidden;">
            <button type="submit">Finished</button>
        </form>

        <script type="module">
            import { startStopwatch } from '../js/functions/stopwatch.js';
            document.addEventListener('DOMContentLoaded', () => {
                startStopwatch();
            });
        </script>
    </body>
</html>
