<?php
session_start();
?>

<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="description" content="Study Examples for Participants">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <link rel="stylesheet" href="/public/css/header.css">
        <link rel="stylesheet" href="/public/css/example.css">
        <meta id="csrf_token" name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>
    
    <body>

        <div class="example-container">
            <h1>Examples of Good and Bad Study Interactions</h1>
            
            <div class="example-section">
                <h2>1. Eye Tracking and Cursor Movement</h2>
                <div class="example-grid">
                    <div class="example-item good">
                        <h3>✓ Good Example</h3>
                        <div class="example-description">
                            <p>User's cursor follows their eye gaze while reading the text. This helps us better understand how you process information and significantly improves the accuracy of our study.</p>
                            <p>• Cursor moves along with text being read</p>
                            <p>• Steady, consistent pace of movement</p>
                            <p>• Natural pauses at paragraph breaks</p>
                            <p>• Vertical scrolling matches reading flow</p>
                        </div>
                    </div>
                    
                    <div class="example-item bad">
                        <h3>✗ Bad Example</h3>
                        <div class="example-description">
                            <p>Cursor remains static while eyes move around, or cursor movements don't match reading pattern. This makes it harder for us to accurately track your reading experience.</p>
                            <p>• Cursor stays in one place while reading</p>
                            <p>• Erratic or jumpy movements</p>
                            <p>• Moving cursor without reading</p>
                            <p>• Random clicking or highlighting</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="example-section">
                <h2>2. AI Interaction Quality</h2>
                <div class="example-grid">
                    <div class="example-item good">
                        <h3>✓ Good Questions</h3>
                        <img src="../media/good_response_01.png" alt="Good evaluation example" class="example-image">
                        <img src="../media/good_response_02.png" alt="Good evaluation example" class="example-image">
                        <div class="example-description">
                            <p>Good questions are open-ended and complex, requiring detailed analysis of a specific topic. They should:</p>
                            <p>• Focus on a specific aspect or problem</p>
                            <p>• Encourage in-depth discussion</p>
                            <p>• Require analysis and critical thinking</p>
                            <p>• Connect multiple concepts together</p>
                            <p>Examples:</p>
                            <p>- "How has LeBron James's playing style evolved throughout his career and influenced modern basketball?"</p>
                            <p>- "What impact has Tom Cruise's choice of roles had on action movie genres since the 1980s?"</p>
                        </div>
                    </div>
                    
                    <div class="example-item bad">
                        <h3>✗ Poor Questions</h3>
                        <img src="../media/bad_response_01.png" alt="Good evaluation example" class="example-image">
                        <img src="../media/bad_response_02.png" alt="Good evaluation example" class="example-image">
                        <div class="example-description">
                            <p>Poor questions are overly simple, vague, or too broad. Avoid questions that:</p>
                            <p>• Can be answered with just yes/no</p>
                            <p>• Are too general or lack focus</p>
                            <p>• Don't require explanation or reasoning</p>
                            <p>• Ask for basic facts only</p>
                            <p>Examples:</p>
                            <p>- "Is LeBron James tall?"</p>
                            <p>- "What movies has Tom Cruise been in?"</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="example-section">
                <h2>3. Learning Summary</h2>
                <div class="example-grid">
                    <div class="example-item good">
                        <h3>✓ Good Summary</h3>
                        <div class="example-description">
                            <p>Clear, specific statement that demonstrates understanding and insight gained from the AI interaction.</p>
                            <p>Examples:</p>
                            <p>• "I learned how LeBron James's leadership style evolved from being primarily score-focused to becoming a more complete floor general who elevates his teammates' performance."</p>
                            <p>• "I discovered how Tom Cruise's commitment to performing his own stunts has influenced modern action filmmaking and raised audience expectations for authentic action sequences."</p>
                            <p>• "I learned how Aziz Ansari's social commentary in 'Master of None' uniquely addresses modern dating and technology through the lens of a millennial Indian-American."</p>
                        </div>
                    </div>
                    
                    <div class="example-item bad">
                        <h3>✗ Poor Summary</h3>
                        <div class="example-description">
                            <p>Vague, oversimplified statements that don't reflect meaningful learning or understanding.</p>
                            <p>Examples:</p>
                            <p>• "LeBron James is good at basketball."</p>
                            <p>• "Tom Cruise makes action movies."</p>
                            <p>• "I learned some things about movies."</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="example-section">
                <h2>4. Response Evaluation</h2>
                <div class="example-grid">
                    <div class="example-item good">
                        <h3>✓ Good Evaluation Practice</h3>
                        <div class="example-description">
                            <p>Carefully reading the response and rating based on relevancy, accuracy, and helpfulness.</p>
                        </div>
                    </div>
                    
                    <div class="example-item bad">
                        <h3>✗ Poor Evaluation Practice</h3>
                        <div class="example-description">
                            <p>Rushing through responses or giving random ratings without proper consideration.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Important Reminders:</h2>
                <ul>
                    <li>Always follow your cursor with your eyes while reading</li>
                    <li>Ask meaningful questions that require detailed responses</li>
                    <li>Take time to properly evaluate AI responses</li>
                    <li>Complete at least three interactions before finishing</li>
                </ul>
            </div>
        </div>

        <footer>
            <p>For technical support: the study administrator</p>
        </footer>
    </body>
</html>
