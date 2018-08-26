const mysql = require('mysql');

var con = mysql.createConnection({
    host: "localhost",
    database: "hc_cc",
    user: "root",
    password: ""
});

module.exports.con = con;

function isAdmin(token, success, error, response) {
    // selects all users with the specified token and the role 'admin'
    if (token === undefined) {
        response.statusCode = 400;
        response.statusMessage = "Bad Request!";
        response.end();

        return;
    }
    con.query("SELECT * FROM users WHERE users.id IN (SELECT user FROM tokens WHERE token=?) AND users.role IN (SELECT id FROM roles WHERE name='admin');", token, (err, res) => {
        if (err) {
            console.log("Error while checking if the specified token is the token of an admin user: " + err);
            internalError(err, response);
            return;
        }
        if (res.length > 0) {
            success();
        } else {
            error(401, "Access denied!");
        }
    });
}

module.exports.isAdmin = isAdmin;

function internalError(err, res) {
    res.statusCode = 503;
    res.statusMessage = "Service unavailable";
    res.end();
}

module.exports.internalError = internalError;

function usernameInUse(username, success, error, response) {
    con.query("SELECT * FROM users WHERE username=?;", username.trim().toLowerCase(), (err, res) => {
        if (err) {
            console.log("Error while checking if username is already in use: " + err);
            internalError(err, response);
            error(true);
            return;
        }
        if (res.length == 0) {
            success();
        } else {
            error(false);
        }
    });
}

module.exports.usernameInUse = usernameInUse;

function emailInUse(email, success, error, response) {
    con.query("SELECT * FROM users WHERE email=?;", email.trim().toLowerCase(), (err, res) => {
        if (err) {
            console.log("Error while checking if email is already in use: " + err);
            internalError(err, response);
            error(true);
            return;
        }
        if (res.length == 0) {
            success();
        } else {
            error(false);
        }
    });
}

module.exports.emailInUse = emailInUse;

function unprocessable(error, res) {
    res.statusCode = 422;
    res.statusMessage = "Unprocessable Entity";
    res.end(error);
}

module.exports.unprocessable = unprocessable;