<?php
$config = json_decode(file_get_contents('../../config/config.json'), true);
include $config['path']['file']['init'] . 'config.php';

// Clear all existing session data for fresh login
session_unset();
session_destroy();

// Start a new session
session_start();
session_regenerate_id(true);

// Initialize fresh CSRF token
if(empty($_SESSION['csrf_token'])){
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
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
        <link rel="stylesheet" href="/public/css/login.css">
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>

    <script type="module" src="/public/js/events/login.js" defer></script>

    <body>
        <div> 
            <div>
                <h1>Instructions:</h1>
                <div class="instructions">
                    Please log in using your Mechanical Turk/Worker ID, as shown in the image below.<br>
                    You are invited to select any number of topics you are familiar with or interested in .<br>
                    The questionaire for necessary personal information, calibration of camera, and consent should take ~7 minutes. <br>
                    Finishing each task will take around 6 minutes (only including the Q.A. session with the AI and follow-up questions).<br>
                    You can come back to do more tasks at a later date. We do not recommend leaving a task while it is incomplete.<br>
                    Calibration happens once for each time you login. <br>
                    Each task can only be completed once.<br>
                    
                    <div style="background-color: #ffeaa7; border-left: 4px solid #e17055; padding: 10px; margin: 10px 0; border-radius: 5px;">
                        <span style="font-size: 16px; color: #2d3436; font-weight: bold;">
                            ⚠️ Important: Use only ONE browser tab at a time. Multiple tabs will cause session conflicts and progress loss.
                        </span>
                    </div>
                    
                    We only support Chrome, Firefox, and Microsoft Edge browsers. Refresh the page, use an incognito window, or clear the cache is login issues occur.<br>
                    Please check Mechanical Turk to see if tasks are still available. If there is an issue submitting a task, email the study administrator. <br>

                    <img src="/public/media/id_example.png" width="200px" height="100px">
                </div>

                <h2>Login</h2>
                <form id="login-form" action="/login" method="POST">
                    <div class="form-group">
                        <label for="username">Mechanical Turk ID: </label>
                        <input id="user_id" name="user_id" type="text" required maxlength="16">
                    </div>

                    <label>Choose options:</label><br>
                    <div class="dropdown">
                        <div id="checkboxDropdown" class="dropdown-checkboxes">
                        <!-- <label><input type="checkbox" name="options" value="91"> Star Trek: Picard (season 3)</label>
                        <label><input type="checkbox" name="options" value="92"> Lily James</label>
                        <label><input type="checkbox" name="options" value="93"> Dhanush</label>
                        <label><input type="checkbox" name="options" value="94"> Mohamed Salah</label>
                        <label><input type="checkbox" name="options" value="95"> Chris Pine</label>
                        <label><input type="checkbox" name="options" value="96"> Nick Lachey</label>
                        <label><input type="checkbox" name="options" value="97"> Anthony Mackie</label>
                        <label><input type="checkbox" name="options" value="98"> Sirhan Sirhan</label>
                        <label><input type="checkbox" name="options" value="99"> Caitlyn Jenner</label>
                        <label><input type="checkbox" name="options" value="100"> March 1st Movement</label>
                        <label><input type="checkbox" name="options" value="101"> Burj Khalifa</label>
                        <label><input type="checkbox" name="options" value="102"> Democratic Party (United States)</label>
                        <label><input type="checkbox" name="options" value="103"> Kathryn Newton</label>
                        <label><input type="checkbox" name="options" value="104"> Depeche Mode</label>
                        <label><input type="checkbox" name="options" value="105"> Party Down</label>
                        <label><input type="checkbox" name="options" value="106"> Mae Martin</label>
                        <label><input type="checkbox" name="options" value="107"> Smile (2022 film)</label>
                        <label><input type="checkbox" name="options" value="108"> Brandon Sklenar</label>
                        <label><input type="checkbox" name="options" value="109"> Korean War</label>
                        <label><input type="checkbox" name="options" value="110"> Anne Heche</label>
                        <label><input type="checkbox" name="options" value="111"> Timothée Chalamet</label>
                        <label><input type="checkbox" name="options" value="112"> Chyna</label>
                        <label><input type="checkbox" name="options" value="113"> Genghis Khan</label>
                        <label><input type="checkbox" name="options" value="114"> Travis Scott</label>
                        <label><input type="checkbox" name="options" value="115"> Wilt Chamberlain</label>
                        <label><input type="checkbox" name="options" value="116"> 2023 G20 New Delhi summit</label>
                        <label><input type="checkbox" name="options" value="117"> Sydney Sweeney</label>
                        <label><input type="checkbox" name="options" value="118"> Alan Turing</label>
                        <label><input type="checkbox" name="options" value="119"> Cillian Murphy</label>
                        <label><input type="checkbox" name="options" value="120"> Elizabeth I</label>
                        <label><input type="checkbox" name="options" value="121"> Charlie Chaplin</label>
                        <label><input type="checkbox" name="options" value="122"> Deepika Padukone</label>
                        <label><input type="checkbox" name="options" value="123"> Walt Disney</label>
                        <label><input type="checkbox" name="options" value="124"> Sidharth Malhotra</label>
                        <label><input type="checkbox" name="options" value="125"> The Last of Us: Left Behind</label>
                        <label><input type="checkbox" name="options" value="126"> Milla Jovovich</label>
                        <label><input type="checkbox" name="options" value="127"> Ireland</label>
                        <label><input type="checkbox" name="options" value="128"> Finland</label>
                        <label><input type="checkbox" name="options" value="129"> Andor (TV series)</label>
                        <label><input type="checkbox" name="options" value="130"> Ram Charan</label>
                        <label><input type="checkbox" name="options" value="131"> Steven Tyler</label>
                        <label><input type="checkbox" name="options" value="132"> Cloud computing</label>
                        <label><input type="checkbox" name="options" value="133"> Ron Howard</label>
                        <label><input type="checkbox" name="options" value="134"> House of the Dragon</label>
                        <label><input type="checkbox" name="options" value="135"> Jennifer Connelly</label>
                        <label><input type="checkbox" name="options" value="136"> Nick Offerman</label>
                        <label><input type="checkbox" name="options" value="137"> Leslie Van Houten</label>
                        <label><input type="checkbox" name="options" value="138"> Google Scholar</label>
                        <label><input type="checkbox" name="options" value="139"> Sinéad Keenan</label>
                        <label><input type="checkbox" name="options" value="140"> John Palmer (criminal)</label>
                        <label><input type="checkbox" name="options" value="141"> John Denver</label>
                        <label><input type="checkbox" name="options" value="142"> David Arquette</label>
                        <label><input type="checkbox" name="options" value="143"> Roman Polanski</label>
                        <label><input type="checkbox" name="options" value="144"> Pelé</label>
                        <label><input type="checkbox" name="options" value="145"> Jeff Bezos</label>
                        <label><input type="checkbox" name="options" value="146"> 2022–23 Premier League</label>
                        <label><input type="checkbox" name="options" value="147"> Borsuk (infantry fighting vehicle)</label>
                        <label><input type="checkbox" name="options" value="148"> Jude Law</label>
                        <label><input type="checkbox" name="options" value="149"> Olusegun Obasanjo</label>
                        <label><input type="checkbox" name="options" value="150"> Morocco</label> -->
                        </div>
                    </div>

                    <button id="login-button" type="submit">Submit</button>
                </form>
            </div>

            <div id="login-warning">
                <p></p>
            </div>
        </div>
    </body>
</html>

<!-- 
"project": "en.wikipedia",
"access": "all-access",
"year": "2023",
"month": "01",
"day": "02",

{"article":"Gary Patterson","views":13139,"rank":971
"article":"Severance (TV_series)","views":13135,"rank":972
"article":"Adam_Sandler","views":13133,"rank":973
"article":"Single-player","views":13123,"rank":974
"article":"John_F._Kennedy","views":13112,"rank":975
"article":"Megan_Fox","views":13112,"rank":975
"article":"Barack_Obama","views":13078,"rank":977
"article":"Cissy_Houston","views":13078,"rank":977
"article":"Hugh_Grant","views":13071,"rank":979
"article":"XXX:_State_of_the_Union","views":13071,"rank":979
"article":"Selena_Gomez","views":13062,"rank":981
"article":"Jake_Fromm","views":13053,"rank":982
"article":"President_of_Brazil","views":13035,"rank":983
"article":"Salman_Khan","views":13033,"rank":984
"article":"Death_and_funeral_of_Pope_Benedict_XVI","views":13028,"rank":985
"article":"Love_Today_(2022_film)","views":13016,"rank":986
"article":"Nikola_Tesla","views":13014,"rank":987
"article":"Helen_McCrory","views":13011,"rank":988
"article":"Salma_Hayek","views":13002,"rank":989
"article":"National_Treasure:_Edge_of_History","views":12998,"rank":990
"article":"Aesculus_glabra","views":12994,"rank":991
"article":"Charlie_Chaplin","views":12961,"rank":992
"article":"Game_of_Thrones","views":12955,"rank":993
"article":"Yo_Gotti","views":12946,"rank":994
"article":"Richard_Madden","views":12946,"rank":994
"article":"Chinese_zodiac","views":12942,"rank":996
"article":"Gisele_Bündchen","views":12942,"rank":996
"article":"Romania","views":12938,"rank":998
"article":"Alexander_the_Great","views":12937,"rank":999
"article":"2022_TCU_Horned_Frogs_football_team","views":12883,"rank":1000} -->



<!-- 
https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/2023/02/01
{"project":"en.wikipedia","access":"all-access","year":"2023","month":"02","day":"01","

{"article":"Sweden","views":10038,"rank":968},
{"article":"François-Henri_Pinault","views":10031,"rank":971},
{"article":"The_Watchful_Eye_(TV_series)","views":10022,"rank":972},
{"article":"Baahubali_2:_The_Conclusion","views":10016,"rank":973}, 
{"article":"BlackRock","views":10011,"rank":974}, 
{"article":"Florence_Pugh","views":9992,"rank":975},
{"article":"Jennifer_Connelly","views":9980,"rank":976},
{"article":"Jack_the_Ripper","views":9979,"rank":977},
{"article":"Auckland_City_FC","views":9963,"rank":978},
{"article":"Library_Genesis","views":9959,"rank":979}, 
{"article":"NATO","views":9958,"rank":980},
{"article":"Jessica_Chastain_on_screen_and_stage","views":9951,"rank":981}, 
{"article":"Bijou_Phillips","views":9950,"rank":982},
{"article":"Ved_(film)","views":9947,"rank":983}, 
{"article":"Wilmer_Valderrama","views":9933,"rank":984},
{"article":"American_Psycho_(film)","views":9928,"rank":985}, 
{"article":"Creature_Commandos","views":9927,"rank":986}
{"article":"Gavi_(footballer)","views":9926,"rank":987}, 
{"article":"COVID-19_pandemic","views":9907,"rank":989}, 
{"article":"Special:MyTalk","views":9906,"rank":990},
{"article":"Urfi_Javed","views":9899,"rank":991},
{"article":"Kate_Winslet","views":9891,"rank":992}, 
{"article":"Generation_X","views":9891,"rank":992}, 
{"article":"Minecraft","views":9885,"rank":994},
{"article":"Kristen_Stewart","views":9883,"rank":995}, 
{"article":"Gerard_Piqué","views":9870,"rank":996}, 
{"article":"Lenny_Kravitz","views":9860,"rank":997}, 
{"article":"February_2","views":9859,"rank":998},
{"article":"Joe_Rogan","views":9859,"rank":998}, 
{"article":"Brandon_Lee","views":9859,"rank":998}]}]} -->

<!-- https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/2023/03/01
{"items":[{"project":"en.wikipedia","access":"all-access","year":"2023","month":"03","day":"01", -->

<!-- 
{Task_id: 91, article: Star Trek: Picard (season 3)}
{Task_id: 92, article: Lily James}
{Task_id: 93, article: Dhanush}
{Task_id: 94, article: Mohamed Salah}
{Task_id: 95, article: Chris Pine}
{Task_id: 96, article: Nick Lachey}
{Task_id: 97, article: Anthony Mackie}
{Task_id: 98, article: Sirhan Sirhan}
{Task_id: 99, article: Caitlyn Jenner}
{Task_id: 100, article: March 1st Movement}
{Task_id: 101, article: Burj Khalifa}
{Task_id: 102, article: Democratic Party (United States)}
{Task_id: 103, article: Kathryn Newton}
{Task_id: 104, article: Depeche Mode}
{Task_id: 105, article: Party Down}
{Task_id: 106, article: Mae Martin}
{Task_id: 107, article: Smile (2022 film)}
{Task_id: 108, article: Brandon Sklenar}
{Task_id: 109, article: Korean War}
{Task_id: 110, article: Anne Heche}
{Task_id: 111, article: Timothée Chalamet}
{Task_id: 112, article: Chyna}
{Task_id: 113, article: Genghis Khan}
{Task_id: 114, article: Travis Scott}
{Task_id: 115, article: Wilt Chamberlain}
{Task_id: 116, article: 2023 G20 New Delhi summit}
{Task_id: 117, article: Sydney Sweeney}
{Task_id: 118, article: Alan Turing}
{Task_id: 119, article: Cillian Murphy}
{Task_id: 120, article: Elizabeth I}
{Task_id: 121, article: Charlie Chaplin}
{Task_id: 122, article: Deepika Padukone}
{Task_id: 123, article: Walt Disney}
{Task_id: 124, article: Sidharth Malhotra}
{Task_id: 125, article: The Last of Us: Left Behind}
{Task_id: 126, article: Milla Jovovich}
{Task_id: 127, article: Ireland}
{Task_id: 128, article: Finland}
{Task_id: 129, article: Andor (TV series)}
{Task_id: 130, article: Ram Charan}
{Task_id: 131, article: Steven Tyler}
{Task_id: 132, article: Cloud computing}
{Task_id: 133, article: Ron Howard}
{Task_id: 134, article: House of the Dragon}
{Task_id: 135, article: Jennifer Connelly}
{Task_id: 136, article: Nick Offerman}
{Task_id: 137, article: Leslie Van Houten}
{Task_id: 138, article: Google Scholar}
{Task_id: 139, article: Sinéad Keenan}
{Task_id: 140, article: John Palmer (criminal)}
{Task_id: 141, article: John Denver}
{Task_id: 142, article: David Arquette}
{Task_id: 143, article: Roman Polanski}
{Task_id: 144, article: Pelé}
{Task_id: 145, article: Jeff Bezos}
{Task_id: 146, article: 2022–23 Premier League}
{Task_id: 147, article: Borsuk (infantry fighting vehicle)}
{Task_id: 148, article: Jude Law}
{Task_id: 149, article: Olusegun Obasanjo}
{Task_id: 150, article: Morocco}