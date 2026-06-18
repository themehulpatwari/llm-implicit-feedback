<?php
include '../../src/init/config.php';

// Check if user is authenticated, redirect to login if not
checkUserAuthentication();
?>

<!DOCTYPE html>

<html>
<head>
        <meta HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <link rel="stylesheet" type="text/css" href="/public/css/style.css">
        <link rel="stylesheet" href="../../node_modules/bootstrap/dist/css/bootstrap.min.css">
        <!-- <script src="./tensorflow.js"></script> -->
        <script src="../../node_modules/WebGazer/dist/webgazer.js"></script>
        <meta id='csrf_token' name="csrf-token" content="<?php echo htmlspecialchars($_SESSION['csrf_token']);?>">
    </head>
    <body LANG="en-US" LINK="#0000ff" DIR="LTR">
      <canvas id="plotting_canvas" width="500" height="500" style="cursor:crosshair;"></canvas>

        <script src="../../node_modules/sweetalert/dist/sweetalert.min.js"></script>

        <script type="module" src="../js/functions/redirect.js"></script>
        <script src="../js/functions/calibrate/main.js"></script>
        <script src="../js/functions/calibrate/calibration.js"></script>
        <script src="../js/functions/calibrate/precision_calculation.js"></script>
        <script src="../js/functions/calibrate/precision_store_points.js"></script>
        <script type='module' src='../js/functions/timeout.js' defer></script>
        <script type='module' src='../js/functions/requests.js' defer></script>
        <script type="module" src="../js/functions/accuracy-post.js"></script>
        <script src="../js/functions/calibrate/resize_canvas.js"></script>
        <script src="../../node_modules/bootstrap/dist/js/bootstrap.bundle.min.js"></script>


        <nav id="webgazerNavbar" class="navbar navbar-expand-lg navbar-default navbar-fixed-top">
          <div class="container-fluid">
            <div class="navbar-header">
              <!-- The hamburger menu button -->
              <button type="button" class="navbar-toggler" data-toggle="collapse" data-target="#myNavbar">
                <span class="navbar-toggler-icon">Menu</span>
              </button>
            </div>
            <div class="collapse navbar-collapse" id="myNavbar">
              <ul class="nav navbar-nav">
                <!-- Accuracy -->
                <li id="Accuracy"><a>Not yet Calibrated</a></li>
                <li><a onclick="Restart()" href="#">Recalibrate</a></li>
              </ul>
            </div>
          </div>
        </nav>
        <!-- Calibration points -->
        <div class="calibrationDiv">
            <input type="button" class="Calibration" id="Pt1"></input>
            <input type="button" class="Calibration" id="Pt2"></input>
            <input type="button" class="Calibration" id="Pt3"></input>
            <input type="button" class="Calibration" id="Pt4"></input>
            <input type="button" class="Calibration" id="Pt5"></input>
            <input type="button" class="Calibration" id="Pt6"></input>
            <input type="button" class="Calibration" id="Pt7"></input>
            <input type="button" class="Calibration" id="Pt8"></input>
            <input type="button" class="Calibration" id="Pt9"></input>
        </div>

        <!-- Modal -->
        <div id="helpModal" class="modal fade" role="dialog">
          <div class="modal-dialog">

            <!-- Modal content-->
            <div class="modal-content">
              <div class="modal-body">
                <img src="../media/calibration.png" width="100%" height="100%" alt="webgazer demo instructions"></img>
              </div>
              <div class="modal-footer">
                <button type="button" id='start_calibration' class="btn btn-primary" data-bs-dismiss="modal" onclick="Restart()">Calibrate</button>
              </div>
            </div>

          </div>
        </div>

        <!-- Latest compiled JavaScript -->


    </body>

</html>



