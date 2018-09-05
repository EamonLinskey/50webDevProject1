console.log("test");
var password = document.getElementById("password"), 
	confirmPassword = document.getElementById("confirmPassword"),
	username = document.getElementById("username");

function validatePassword(){
	console.log("validating")
  if(password.value != confirmPassword.value) {
    confirmPassword.setCustomValidity("Passwords Don't Match");
  } else {
    confirmPassword.setCustomValidity('');
  }
}

password.onchange = validatePassword;
confirmPassword.onkeyup = validatePassword;
