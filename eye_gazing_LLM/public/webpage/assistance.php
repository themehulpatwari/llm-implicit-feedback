<?php
session_start();
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="description" content="Study Instructions for Participants">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <link rel="stylesheet" href="/public/css/header.css">
        <link rel="stylesheet" href="/public/css/instruction.css">
        <!-- <script type="module" src="/public/js/events/consent.js" defer></script> -->
        <script type='module' src='../js/functions/timeout.js' defer></script>
        <meta id="csrf_token" name="csrf-token" content="3ebee3dd205044a29f84d586276f2b401de4ab7ece04a088e4b635dc560a4980">
    </head>
    
    <body>
        <header>
            <nav class="navbar">
            <div class="nav-links">
                <a href="/public/webpage/example.php" target="_blank">Examples</a>
            </div>
            </nav>
        </header>

        <div class="container">
            <h1>Website Instructions for Participants</h1>
            <p>Welcome to our study! Please carefully follow the instructions below. Remember, you can exit the task at any time, but you will only receive your payment code if you complete the entire task.</p>

            <div class="section" style="background-color: #f8f9fa; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0;">
                <h3 style="color: #dc3545; margin-top: 0;">⚠️ Important Notice</h3>
                <p style="margin-bottom: 0;">Please use only one browser tab during the study to avoid losing progress.</p>
            </div>

            <div class="section">
                <p>This study uses your <span class="highlight">webcam</span> and <span class="highlight">mouse movement</span>. To increase the accuracy of our eye-tracking software, we kindly ask you to <span class="highlight">move your cursor with your gazing point whenever possible</span>. Each task will include brief instructions to further guide you.</p>
            </div>

            <p>Before you click the Next Step, make sure to click <span class="highlight">Examples</span> to check some do's and don'ts. If working on a laptop, <span class="highlight"> don't ever close the laptop while working with the AI or calibrating</span>, this will mess up the eye-gazing behvavior.</p>

            <p><span class="highlight">Important: Do NOT refresh the page during the study</span>, as this may disrupt your progress and eye-tracking calibration.</p>

            <p>Lastly, an inactive mouse for 30 minutes will redirect you to the login screen for inactivity. We support only select browsers (Chrome, Firefox, Edge) with troubleshooting at the bottom.</p>

            <div class="section">
                <h2>1. Calibration</h2>
                <ul>
                    <li>When prompted, click <span class="highlight">Allow</span> to enable camera access for calibration.</li>
                    <li>Left-click the <span class="highlight">red circle buttons</span> on your screen with your cursor until it becomes yellow. <span class="highlight">Make sure your eyes track your cursor all the time during the calibration</span>.  </li>
                    <li>After the calibration, you will receive an accuracy score. If your accuracy is low, try to better track your cursor, get closer to the screen, change the lighting condition in your room, or use a better camera. If you are not able to reach the desired calibration accuracy, you are not qualified to do the tasks.</li>
                    <li>The camera screen box may move during this process; this is normal.</li>
                    <li>Once calibration is complete successfully, the page will automatically redirect you.</li>
                    <li>More detailed instructions will be shown on the task page</li>
                </ul>
            </div>

            <div class="section">
                <h2>2. Interaction with AI</h2>
                <p>You will be redirected to one of two tasks:</p>

                <h3>General Guidelines for AI Interaction</h3>
                <ul>
                    <li>Each time you ask a question in the search box, the AI will respond in the box below.</li>
                    <li>Please keep in mind that <span class="highlight">refreshing the page, switch to instruction page, or asking another question will delete the previous question and response on the screen, but the AI will know all the previous questions you have asked and adjust its response accordingly.</span></li>
                    <li>Please judge the response based on its overall quality, which includes but not limit to relevancy to your question, factuality (if you are able to judge), informativeness, and helpfulness. </li>
                    <li>Please notice that AI response might be cut short or include some markers such as using ** to highlight the text. Please do NOT lower your score because you think the response is not finished or these markers are not displayed properly. </li>
                    <li>We encourage full dialogues with the AI. Ask as many questions as you like, but note that <span class="highlight">payment is not based on the number of questions you ask.</span></li>
                    <li>You must interact with the AI and ask at least three questions before moving on to the next step.</span></li>
                    <li>If an AI error comes up, come back after an hour to try again. If another error occurs, report to the study administrator with the error code.</li>
                    <li><span class="highlight">Please try to follow your cursor with your eye gaze point while reading while keeping you head in the camera box (when the border is green).</span></li>
                </ul>

                <h3>Option A</h3>
                <ul>
                    <li>A question box will appear for you to interact with the AI model.</li>
                    <li>Type your question or talk to the AI. Press <span class="highlight">Enter</span> to send your question.</li>
                    <li>The AI will respond after a few seconds. After each response, rate your satisfaction with the response.</li>
                    <li>Starting from your second question, you will see a <span class="highlight">comparison section</span> showing both the previous AI answer and the current AI answer. Please select whether the current answer is better or worse than the previous one using the dropdown menu.</li>
                    <li>Click the <span class="highlight">Finished</span> button to move to the next page.</li>
                </ul>

                <h3>Option B</h3>
                <ul>
                    <li>Similar to Option A, but you will receive responses from <span class="highlight">two AI models</span>.</li>
                    <li>Rate your satisfaction with each response and indicate which response you prefer.</li>
                    <li>Click the <span class="highlight">Finished</span> button to proceed.</li>
                </ul>
            </div>

            <div class="section">
                <h2>3. Conversation Summary</h2>
                <ul>
                    <li>Summarize the conversation using one or two sentence(s) in the text box provided. The summary should focus on what you learned on the topic and include nothing about the AI.</li>
                    <li>Click <span class="highlight">Submit</span> to proceed to the next page.</li>
                </ul>
            </div>

            <div class="section">
                <h2>4. Past Question and Response</h2>
                <ul>
                    <li>You will be shown a randomly chosen <span class="highlight">past question</span> and the <span class="highlight">AI’s response</span>.</li>
                    <li>Copy the sentence you felt was most important and paste it into the provided box.</li>
                    <li>(Optional) Add feedback in the <span class="highlight">Feedback Box</span> if needed. Click <span class="highlight">Submit</span> when you are done.</li>
                </ul>
            </div>

            <div class="section">
                <h2>5. Payment Code</h2>
                <ul>
                    <li>A unique passcode will be displayed. <span class="highlight">Store this passcode somewhere safe</span> and submit the passcode to MTurk to receive your payment. You will not be able to retrieve it later.</li>
                    <li>Important: Please do NOT submit one passcode multiple times. We might be forced to reject your submission if you do that.</li>
                    <li>If you really have issues with passcode, please contact the study administrator.</li>
                    <li>Do not refresh this page. Click <span class="highlight">Finished</span> to complete the task.</li>
                </ul>
            </div>

            <div class="section">
                <h2>6. Troubleshooting: Clearing Cookies</h2>
                <p>If you experience issues with the study website, such as buttons not working or pages not loading correctly, try clearing cookies for <span class="highlight">the study website</span> using the instructions below for your browser.</p>

                <h3>Chrome</h3>
                <ul>
                    <li>On your computer, open Chrome.</li>
                    <li>At the top right, select <b>More</b> (three dots) → <b>Settings</b>.</li>
                    <li>Go to <b>Privacy and security</b> → <b>Third-party cookies</b>.</li>
                    <li>Select <b>See all site data and permissions</b>.</li>
                    <li>At the top right, search for <span class="highlight">the study website</span>.</li>
                    <li>To the right of the site, select <b>Delete</b> (trash icon).</li>
                    <li>To confirm, select <b>Delete</b> again.</li>
                </ul>

                <h3>Edge</h3>
                <ul>
                    <li>Open the <b>Edge</b> browser, select <b>Settings and more</b> (three dots) → <b>Settings</b>.</li>
                    <li>Go to <b>Cookies and site permissions</b>.</li>
                    <li>Under <b>Cookies and data stored</b>, select <b>Manage and delete cookies and site data</b>.</li>
                    <li>Click <b>See all cookies and site data</b>.</li>
                    <li>Search for <span class="highlight">the study website</span>.</li>
                    <li>Select the down arrow next to the site, then click <b>Delete</b>.</li>
                </ul>

                <h3>Firefox</h3>
                <ul>
                    <li>In the Menu bar at the top of the screen, click <b>Firefox</b> → <b>Preferences</b> (or <b>Settings</b> on newer versions).</li>
                    <li>Select the <b>Privacy & Security</b> panel.</li>
                    <li>Under <b>Cookies and Site Data</b>, click <b>Manage Data…</b>.</li>
                    <li>In the search field, type <span class="highlight">the study website</span>.</li>
                    <li>Select the site and click <b>Remove Selected</b> → <b>Save Changes</b>.</li>
                </ul>
            </div>


            <p>Thank you for participating in our research! Your contributions are invaluable.</p>
            <p>After reading the above message, please click link on the upper-left corner to continue. You can always check this instruction page by clicking the link on the upper-left corner</p>
        </div>

        <footer>
            For any additional help/inquiries: the study administrator
        </footer>


        <!-- <script>
            document.addEventListener('DOMContentLoaded', function() {
                var previousPage = document.referrer;
                var taskLink = document.getElementById('task');
                if (taskLink) {
                    taskLink.href = previousPage;
                }
            });
        </script> -->
    

</body></html>