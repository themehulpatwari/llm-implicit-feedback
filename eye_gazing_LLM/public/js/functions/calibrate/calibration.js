// import { postRequest } from "./requests.js";

var PointCalibrate = 0;
var CalibrationPoints={};

// Find the help modal
var helpModal;

/**
 * Clear the canvas and the calibration button.
 */
function ClearCanvas(){
  document.querySelectorAll('.Calibration').forEach((i) => {
    i.style.setProperty('display', 'none');
  });
  var canvas = document.getElementById("plotting_canvas");
  canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
}

/**
 * Show the instruction of using calibration at the start up screen.
 */
function PopUpInstruction(){
  ClearCanvas();
  swal({
    title:"Calibration",
    text: "Please click on each of the 9 points on the screen. You must click on each point 5 times till it goes yellow. This will calibrate your eye movements.",
    buttons:{
      cancel: false,
      confirm: true
    }
  }).then(isConfirm => {
    ShowCalibrationPoint();
  });

}
/**
  * Show the help instructions right at the start.
  */
function helpModalShow() {
    if(!helpModal) {
        helpModal = new bootstrap.Modal(document.getElementById('helpModal'))
    }
    helpModal.show();
}

function calcAccuracy() {
  // show modal
  // notification for the measurement process
  swal({
    title: "Calculating measurement",
    text: "After clicking OK, please move your mouse to the yellow dot in the middle of the screen and stare at it. Please stare at the middle dot for the next 5 seconds. This will allow us to calculate the accuracy of our predictions.",
    closeOnEsc: false,
    allowOutsideClick: false,
    closeModal: true
  }).then(() => {
    // makes the variables true for 5 seconds & plots the points
  
    store_points_variable(); // start storing the prediction points
  
    sleep(5000).then(() => {
      stop_storing_points_variable(); // stop storing the prediction points
      const required_precision = 70; //change PRECISION HERE
      var past50 = webgazer.getStoredPoints(); // retrieve the stored points
      var precision_measurement = calculatePrecision(past50);
      var accuracyLabel = "<a>Accuracy | " + precision_measurement + "%</a>";
      document.getElementById("Accuracy").innerHTML = accuracyLabel; // Show the accuracy in the nav bar.
      swal({
        title: "Your accuracy measure is " + precision_measurement + "%",
        text: precision_measurement > required_precision ? "" : "Accuracy is less than " + required_precision + "%. You will be taken back to calibration again.",
        allowOutsideClick: false,
        buttons: {
          confirm: true,
        }
      }).then(async () => {
        if (precision_measurement > required_precision) {
          const token = document.getElementById('csrf_token').getAttribute('content');
          console.log("token=", token);
          
          // Create and dispatch a custom event before making the POST request
          const beforePostEvent = new CustomEvent("beforeAccuracyPost", {
            detail: { 
              accuracy: precision_measurement,
              token: token
            }
          });
          document.dispatchEvent(beforePostEvent);

          const redirectEvent = new CustomEvent("triggerRedirect", {
            detail: { token },
          });
          document.dispatchEvent(redirectEvent); // Trigger the event
        } else {
          //clear the calibration & hide the last middle button
          document.getElementById("Accuracy").innerHTML = "<a>Not yet Calibrated</a>";
          webgazer.clearData();
          ClearCalibration();
          ClearCanvas();
          ShowCalibrationPoint();
        }
      });
    });
  });
}

function calPointClick(node) {
    const id = node.id;

    if (!CalibrationPoints[id]){ // initialises if not done
        CalibrationPoints[id]=0;
    }
    CalibrationPoints[id]++; // increments values

    if (CalibrationPoints[id]==5){ //only turn to yellow after 5 clicks
        node.style.setProperty('background-color', 'yellow');
        node.setAttribute('disabled', 'disabled');
        PointCalibrate++;
    }else if (CalibrationPoints[id]<5){
        //Gradually increase the opacity of calibration points when click to give some indication to user.
        var opacity = 0.2*CalibrationPoints[id]+0.2;
        node.style.setProperty('opacity', opacity);
    }

    //Show the middle calibration point after all other points have been clicked.
    if (PointCalibrate == 8){
        document.getElementById('Pt5').style.removeProperty('display');
    }

    if (PointCalibrate >= 9){ // last point is calibrated
        // grab every element in Calibration class and hide them except the middle point.
        document.querySelectorAll('.Calibration').forEach((i) => {
            i.style.setProperty('display', 'none');
        });
        document.getElementById('Pt5').style.removeProperty('display');

        // clears the canvas
        var canvas = document.getElementById("plotting_canvas");
        canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

        // Calculate the accuracy
        calcAccuracy();
    }
}

/**
 * Load this function when the index page starts.
* This function listens for button clicks on the html page
* checks that all buttons have been clicked 5 times each, and then goes on to measuring the precision
*/
//$(document).ready(function(){
function docLoad() {
  ClearCanvas();
  helpModalShow();
    
    // click event on the calibration buttons
    document.querySelectorAll('.Calibration').forEach((i) => {
        i.addEventListener('click', () => {
            calPointClick(i);
        })
    })
};
window.addEventListener('load', docLoad);

/**
 * Show the Calibration Points
 */
function ShowCalibrationPoint() {
  document.querySelectorAll('.Calibration').forEach((i) => {
    i.style.removeProperty('display');
  });
  // initially hides the middle button // uncomment later
  document.getElementById('Pt5').style.setProperty('display', 'none');
}

/**
* This function clears the calibration buttons memory
*/
function ClearCalibration(){
  // Clear data from WebGazer

  document.querySelectorAll('.Calibration').forEach((i) => {
    i.style.setProperty('background-color', 'red');
    i.style.setProperty('opacity', '0.2');
    i.removeAttribute('disabled');
  });

  CalibrationPoints = {};
  PointCalibrate = 0;
}

// sleep function because java doesn't have one, sourced from http://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}
