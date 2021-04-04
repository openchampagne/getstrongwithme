function switch_units(units) {
    if (units == 'Imperial') {
       document.getElementById('units').textContent = 'Metric';
       document.getElementById('unit-height').textContent = 'm';
       document.getElementById('unit-weight').textContent = 'kg';
 }
    else {
       document.getElementById('units').textContent = 'Imperial';
       document.getElementById('unit-height').textContent = 'in';
       document.getElementById('unit-weight').textContent = 'lbs';
    }
 }


function bmi_status(bmi) {
    if (bmi < 18.5) {
        document.getElementById('bmi-status').textContent = 'Your BMI is ' + bmi + ' which is Underweright. Speak with your doctor to determine if you need to gain weight.';
    }
    else if (bmi >= 18.5 && bmi <= 24.9) {
        document.getElementById('bmi-status').textContent = 'Your BMI is ' + bmi + ' which is Healthy!';
    }
    else if (bmi >= 25.0 && bmi <= 29.9) {
        document.getElementById('bmi-status').textContent = 'Your BMI is ' + bmi + ' which is Overweight. Being overweight can lead to a higher chance of heart and other health issues. Soeak to your doctor to determine the healthiest ways for you to lose weight.';        
    }
    else if (bmi > 30.0){
        document.getElementById('bmi-status').textContent = 'Your Bmi is ' + bmi + ' which classifies as Obese. Obesity can be very dangerous and cause chronic diesases. Speak with your doctor to determine the healthiest ways for you to lose weight';
    }
}

function calculate_bmi(units, height, weight) {
    console.log('Height = %s Weight = %s Units = %s', height, weight, units);
    var bmi = (weight/(height**2));
    if (units == 'Imperial') {
       bmi = (bmi*703);
    }
    bmi = bmi.toFixed(1)
    console.log(bmi);
    if (bmi == NaN) {
       document.getElementById('bmi').textContent = 'Enter your height and weight above to calculate your BMI!';
    }
    else {
        document.getElementById('bmi').textContent = bmi;
    }
    bmi_status(bmi)
}