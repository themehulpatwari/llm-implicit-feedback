const url = window.location.pathname;
let obj = {w: false, c: false, h: false};

if(url === "/public/webpage/calibration.php"){
    obj = {w: true, c: true, h: false, p: false};
} else if(url === "/public/webpage/pointwise.php"){
    obj = {w: true, c: false, h: false, p: false};
} else if(url === "/public/webpage/pairwise.php"){
    obj = {w: true, c: false, h: false, p: true};
}

export const settings = obj;