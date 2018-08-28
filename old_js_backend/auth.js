"use strict";
const server = require('./main.js');
const db = require('./databaseFunctions.js');
const sha512 = require('sha512');
const responder = require('./response.js');

server.on("getUser", obj => { // get information about an account
    if (obj.req.headers['access-token'] === undefined) {
        responder.respond(obj.res, 400, "Bad request!", "Token not specified!");
        return;
    }
    db.con.query("SELECT user FROM tokens WHERE token=? AND broken='0' AND CURRENT_TIMESTAMP < expires;", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            db.internalError(err, obj.res);
            return;
        }
        if (res.length == 1) {
            db.con.query("SELECT publicId, username, email, lastLogin, created, role FROM users WHERE id=?;", res[0].user, (err, result) => {
                if (err) {
                    db.internalError(err, obj.res);
                    return;
                }
                db.con.query("SELECT name, description FROM roles WHERE id=?;", result[0].role, (err, roleResult) => {
                    if (err) {
                        db.internalError(err, obj.res);
                        return;
                    }
                    result[0].role = roleResult[0];
                    responder.respond(obj.res, 200, "Ok!", undefined, JSON.stringify(result[0]));
                });
            });
        } else {
            responder.respond(obj.res, 403, "Forbidden!");
        }
    });
});

server.on("login", obj => { // login
    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        responder.respond(obj.res, 400, "Bad request!", "Invalid JSON format!");
        return;
    }
    if (data.username === undefined || data.username.trim().length === 0) {
        //no username specified
        db.unprocessable("You have to enter a username!", obj.res);
        return;
    }
    if (data.password === undefined || data.password.length === 0) {
        //no password specified
        db.unprocessable("You have to enter a password!", obj.res);
        return;
    }

    db.con.query("SELECT id FROM users WHERE username=? AND password=?;", [data.username.trim().toLowerCase(), sha512(data.password).toString('hex')], (err, res) => {
        if (err) {
            db.internalError(err, obj.res);
            return;
        }
        if (res.length === 1) {
            generateToken((token) => {
                db.con.query("INSERT INTO tokens SET user=?, token=?, expires=NOW() + INTERVAL 6 HOUR;", [res[0].id, token], (err, result) => {
                    if (err) {
                        db.internalError(err, obj.res);
                        return;
                    }
                    responder.respond(obj.res, 200, "OK!", undefined, ["Logged in successfully!", {token: token}]);
                });
            }, obj.res);
        } else {
            //wrong login data
            responder.respond(obj.res, 401, "Unauthorized!", "Password and username do not match!");
        }
    });
});

server.on("logout", obj => { // logout
    // logout
    if (obj.req.headers['access-token'] === undefined) {
        responder.respond(obj.res, 400, "Bad request!", "Token not specified!");
        return;
    }
    db.con.query("UPDATE tokens SET broken='1' WHERE token=?", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            db.internalError(err, obj.res);
            return;
        }
        if (res.affectedRows == 1) {
            responder.respond(obj.res, 200, "Ok!", undefined, "Logged out successfully!");
        } else {
            responder.respond(obj.res, 404, "Not found!", "Invalid token!");
        }
    });
});

function generateToken(success, response) {
    var result = "";
    for (let i = 0; i < 128; i++) {
        result += String.fromCharCode(Math.floor(Math.random() * (122 - 65 + 1) + 65));
    }
    db.con.query("SELECT * FROM tokens WHERE token=?", result, (err, res) => {
        if (err) {
            db.internalError(err, response);
            return;
        }
        if (res.length == 0) {
            success(result);
        } else {
            generateToken(success, response);
        }
    });
}