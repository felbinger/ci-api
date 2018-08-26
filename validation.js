function checkUsername(username) {
    if (username === undefined || username.trim().length == 0) {
        return false;
    } else {
        return true;
    }
}

module.exports.checkUsername = checkUsername;

function checkEmail(email) {
    if (email === undefined || email.trim().length == 0) {
        return false;
    } else {
        return true;
    }
}

module.exports.checkEmail = checkEmail;

function checkEmailFormat(email) {
    var reg = /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
    if (reg.test(email.trim())) {
        return true;
    } else {
        return false;
    }
}

module.exports.checkEmailFormat = checkEmailFormat;

function checkPassword(password) {
    if (password === undefined || password.length < 8) {
        return false;
    } else {
        return true;
    }
}

module.exports.checkPassword = checkPassword;