"use strict";
const server = require('./main.js');
const db = require('./databaseFunctions.js');
const sha512 = require('sha512');

server.on("getUser", obj => { // get information about an account
    if (obj.req.headers['access-token'] === undefined) {
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
        obj.res.end();
        return;
    }
    db.con.query("SELECT user FROM tokens WHERE token=? AND broken='0' AND CURRENT_TIMESTAMP < expires;", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            console.log("Error while selecting token!");
            db.internalError(err, obj.res);
            return;
        }
        if (res.length == 1) {
            db.con.query("SELECT publicId, username, email, lastLogin, created, role FROM users WHERE id=?;", res[0].user, (err, result) => {
                if (err) {
                    console.log("Error while selecting user with the id " + res[0].user);
                    db.internalError(err, obj.res);
                    return;
                }
                db.con.query("SELECT name, description FROM roles WHERE id=?;", result[0].role, (err, roleResult) => {
                    if (err) {
                        console.log("Error while selecting role with id " + result[0].role);
                        db.internalError(err, obj.res);
                        return;
                    }
                    result[0].role = roleResult[0];
                    obj.res.end(JSON.stringify(result[0]));
                });
            });
        } else {
            obj.res.statusCode = 403;
            obj.res.statusMessage = "Forbidden";
            obj.res.end();
        }
    });
});

server.on("login", obj => { // login
    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
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
            console.log("Error while selecting all users with username " + data.username.trim() + " and the specified password!");
            db.internalError(err, obj.res);
            return;
        }
        if (res.length === 1) {
            generateToken((token) => {
                db.con.query("INSERT INTO tokens SET user=?, token=?, expires=NOW() + INTERVAL 6 HOUR;", [res[0].id, token], (err, result) => {
                    if (err) {
                        console.log("Error while adding new token to database!");
                        db.internalError(err, obj.res);
                        return;
                    }
                    obj.res.end("Logged in successfully!\n" + token);
                });
            }, obj.res);
        } else {
            //wrong login data
            obj.res.statusCode = 401;
            obj.res.statusMessage = "Unauthorized";
            obj.res.end("Password and username do not match!");
        }
    });
});

server.on("logout", obj => { // logout
    // logout
    if (obj.req.headers['access-token'] === undefined) {
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
        obj.res.end();
        return;
    }
    db.con.query("UPDATE tokens SET broken='1' WHERE token=?", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            console.log("Error while setting token to broken=1!")
            db.internalError(err, obj.res);
            return;
        }
        if (res.affectedRows == 1) {
            obj.res.end("Logged out successfully!");
        } else {
            obj.res.statusCode = 404;
            obj.res.statusCode = "Not Found!";
            obj.res.end("Invalid token!");
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
            console.log("Error while checking if token already exists!");
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