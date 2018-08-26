const mysql = require('mysql');
const responder = require('./response.js');

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
        error(400, "Bad request!", "Token not specified!");
        return;
    }
    con.query("SELECT * FROM users WHERE users.id IN (SELECT user FROM tokens WHERE token=?) AND users.role IN (SELECT id FROM roles WHERE name='admin');", token, (err, res) => {
        if (err) {
            internalError(err, response);
            return;
        }
        if (res.length > 0) {
            success();
        } else {
            error(401, "Access denied!", "You need to be admin in order to perform this request!");
        }
    });
}

module.exports.isAdmin = isAdmin;

function internalError(err, res) {
    console.log("DB - Internal error: " + err);
    responder.respond(res, 503, "Service unavailable!");
}

module.exports.internalError = internalError;

function usernameInUse(username, success, error, response) {
    con.query("SELECT * FROM users WHERE username=?;", username.trim().toLowerCase(), (err, res) => {
        if (err) {
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