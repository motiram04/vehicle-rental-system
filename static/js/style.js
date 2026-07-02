function togglePassword(){
    const password = document.getElementById("password");
    const icon = document.getElementById("eyeIcon");

    if(password.type === "password"){
        password.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        password.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}

function togglePasswordField(id, eye){
    const input = document.getElementById(id);
    const icon = document.getElementById(eye);

    if(input.type === "password") {
        input.type = "text";
        icon.classList.replace("fa-eye", "fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.replace("fa-eye-slash", "fa-eye");
    }
}

function checkStrength(){
    const password = document.getElementById("password").value;
    const strength = document.getElementById("strength");

    if(password.length < 6){
        strength.innerHTML = "<span class='text-red-500'>Weak Password</span>";
    } else if(password.length < 10){
        strength.innerHTML = "<span class='text-yellow-500'>Medium Password</span>";
    } else {
        strength.innerHTML = "<span class='text-green-600'>Strong Password</span>";
    }
}
