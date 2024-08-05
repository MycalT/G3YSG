// setup gauges 12 Oct2023
var displayOpts = {
    angle: -0.2, // The span of the gauge arc
    lineWidth: 0.2, // The line thickness
    radiusScale: 0.97, // Relative radius
    pointer: {
        length: 0.41, // // Relative to gauge radius
        strokeWidth: 0.082, // The thickness
        color: '#000000' // Fill color
    },
    limitMax: true,     // If false, max value increases automatically if value > maxValue
    limitMin: true,     // If true, the min value of the gauge will be fixed
    highDpiSupport: true,     // High resolution support
    staticLabels: {
        font: "10px sans-serif",  // Specifies font
        labels: [-20, -10, 0, 10, 20, 25, 30],  // Print labels at these values
        color: "#000000",  // Optional: Label text color
        fractionDigits: 0  // Optional: Numerical precision. 0=round off.
    },
    staticZones: [
        {strokeStyle: "#FFDD00", min: -20, max: 00, height: 1}, // Yellow
        {strokeStyle: "#30B32D", min: 00, max: 30, height: 1.1}, // Green
        {strokeStyle: "#F03E3E", min: 30, max: 35, height: 1.2},  // Red
    ],
    renderTicks: {
        divisions: 11,
        divWidth: 1.1,
        divLength: 0.7,
        divColor: "#333333",
        subDivisions: 5,
        subLength: 0.5,
        subWidth: 0.6,
        subColor: "#666666"
    },

};
var target = document.getElementById('fwdGauge');
var gauge = new Gauge(target).setOptions(displayOpts);
gauge.maxValue = 35;
gauge.minValue = -20;
gauge.animationSpeed = 10;
gauge.set(0);

var revTarget = document.getElementById('revGauge');
var revGauge = new Gauge(revTarget).setOptions(displayOpts);
revGauge.maxValue = 35;
revGauge.minValue = -20;
revGauge.animationSpeed = 10;
revGauge.set(0);

gatherDataAjaxRunning = false;
function gatherData(){
    // stop overlapping requests
    if(gatherDataAjaxRunning) return;

    gatherDataAjaxRunning = true;
    let postData = {
        "action": "readData"
    };
    $.post( "/api", postData, function( data ) {
        // handle gauge
 
        fwd = parseFloat(data.fwd_value);
	gauge.set(fwd);

	//bg-primary  blue,  bg-success  green,  bg-warning yellow, bg-danger red 
	// if no class added nothing displayed - so used for no TX to removed noise floor readings 
        $('#fwdValue').html(fwd.toFixed(1));
        $('#fwdValue').removeClass(["bg-primary", "bg-success", "bg-warning", "bg-danger"]);
        if(fwd <= -40) {
            ;
        }
	else if(fwd <= 0) {
            $('#fwdValue').addClass("bg-warning");
        }
        else if(fwd <= 30) {
            $('#fwdValue').addClass("bg-success");
        }
        else {
            $('#fwdValue').addClass("bg-danger");
        }

        // handle rev gauge
        rev = parseFloat(data.rev_value);
        revGauge.set(rev);
        $('#revValue').html(rev.toFixed(1));
        $('#revValue').removeClass(["bg-primary", "bg-success", "bg-warning", "bg-danger"]);
	if(fwd <= -40) {
            ;
        }
	else if(rev <= 0) {
            $('#revValue').addClass("bg-warning");
        }
	else if(rev <= 10) {
            $('#revValue').addClass("bg-success");
        }
        else {
            $('#revValue').addClass("bg-danger");
        }

        // handle rgb leds
        for(count = 0; count < 8; count ++){
            let colour = "rgb(" + (parseInt(data.rgb_leds[count][0])*2) + ", "
                    + (parseInt(data.rgb_leds[count][1])*2) + ", "
                    + (parseInt(data.rgb_leds[count][2])*2);
            $("#rgb_" + count).css("background-color", colour);
        }

        // allow next data gather call
        gatherDataAjaxRunning = false;

    });
}

function SetAction(touched) {
    let postData = {
    "action": "SetAction",
    "touched": touched
    };
    $.post( "/api", postData, function( data ) {
        console.log(data);
        if (data.status == "OK"){
            // set colour from json array
            if (data.dev_states.dev_one){
                $("#dev-state").css("background-color", "rgb(0,0,255)");
            }
            else if (data.dev_states.dev_two){
                $("#dev-state").css("background-color", "rgb(255,255,0)");
            }
            else if (data.dev_states.dev_3){
                $("#dev-state").css("background-color", "rgb(0,255,0)");
            }
            else {
                $("#dev-state").css("background-color", "rgb(0,0,0)");
            }
        }
        else {
            alert("Error setting led colour");
        }
    });
}

var rgb_ajax_in_progress = false;

function set_rgb_colour() {
    console.log("set_rgb_colour")
    // do not start new request until previous finished
    if(rgb_ajax_in_progress) return;

    let postData = {
        "action": "setRgbColour",
        "red": $("#rgb_red").val(),
        "green": $("#rgb_green").val(),
        "blue": $("#rgb_blue").val()
    };
    rgb_ajax_in_progress = true;
    $.post( "/api", postData, function( data ) {
        console.log(data);
        rgb_ajax_in_progress = false // allow next call
        if (data.status == "OK"){
            // set colour from json array
            let colour = "rgb(" + (parseInt(data.rgb_colours.red)*2) + ", "
                + (parseInt(data.rgb_colours.green)*2) + ", "
                + (parseInt(data.rgb_colours.blue)*2);
            for(count = 0; count < 4; count ++){
                $("#rgb_" + count).css("background-color", colour);
            }
        }
        else {
            alert("Error setting led colour");
        }

    });
}

var dataTimer;
$( document ).ready(function() {
    set_rgb_colour(); // initialise rgb display
    dataTimer = setInterval(window.gatherData,200); // call data every 0.2 seconds
});