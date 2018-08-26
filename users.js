"use strict";
const server = require("./main.js");
const db = require("./databaseFunctions.js");
const sha512 = require('sha512');
const validate = require('./validation.js');
const url = require('url');
const uuidv4 = require('uuid/v4');
const responder = require('./Response.js');

server.on("getAll", obj => { // GET /api/users - ADMIN: get data of all users
    db.isAdmin(obj.req.headers["access-token"],
        () => {
            // is admin
            db.con.query(
                "SELECT username, publicID, email, lastLogin, created, role FROM users;",
                (err, res) => {
                    if (err) {
                        console.log("Error while selecting all users: " + err);
                        db.internalError(err, obj.res);
                        return;
                    }
                    for (let i = 0; i < res.length; i++) {
                        db.con.query(
                            "SELECT name, description FROM roles WHERE id=?;", res[i].role,
                            (error, result) => {
                                if (err) {
                                    console.log("Error while selecting role of user " + res[i].username + ": " + error);
                                    db.internalError(error, obj.res);
                                    return;
                                }
                                res[i].role = result[0];
                                if (i === res.length - 1) {
                                    obj.res.end(JSON.stringify(res));
                                }
                            }
                        );
                    }
                }
            );
        },
        (code, message) => {
            //is not admin
            obj.res.statusCode = code;
            obj.res.statusMessage = message;
            obj.res.end();
        },
        obj.res
    );
});

server.on("register", obj => { // register a new user
    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
    }

    if (!validate.checkUsername(data.username)) {
        // username length not ok
        db.unprocessable("Username not long enough!", obj.res);
        return;
    }

    if (!validate.checkEmail(data.email)) {
        // email length not ok
        db.unprocessable("Email not specified!", obj.res);
        return;
    }

    if (!validate.checkEmailFormat(data.email)) {
        // email format not ok
        db.unprocessable("Invalid email!", obj.res);
        return;
    }

    if (!validate.checkPassword(data.password)) {
        //password not long enough
        db.unprocessable("The password has to be at least 8 characters long!", obj.res);
        return;
    }

    db.usernameInUse(
        data.username.trim(),
        () => {
            //username not used
            db.emailInUse(
                data.email.trim(),
                () => {
                    //create Account
                    var insertionData = {
                        publicID: generateUUID4(),
                        username: data.username.trim().toLowerCase(),
                        email: data.email.trim().toLowerCase(),
                        password: sha512(data.password).toString('hex')
                    };
                    db.con.query(
                        "INSERT INTO users SET ?", insertionData,
                        (err, res) => {
                            if (err) {
                                console.log("Error while creating account " + data.username);
                                db.internalError(err, obj.res);
                                return;
                            }
                            console.log(
                                "User " + data.username.trim() + " created successfully!"
                            );
                            obj.res.end();
                            // Todo: call GET Methode!
                        }
                    );
                },
                done => {
                    // email in use
                    if (!done) {
                        db.unprocessable("Email already in use!", obj.res);
                    }
                },
                obj.res
            );
        },
        done => {
            //username in use
            if (!done) {
                db.unprocessable("The username is already in use!", obj.res);
            }
        },
        obj.res
    );
});

function generateUUID4() {
    return uuidv4();
    // todo: prüfen ob schon vorhanden
}


server.on("getUserByUUID", obj => { // ADMIN: get data of user by UUID
    if (db.isAdmin(obj.req.headers['access-token'], () => {
        // user is admin
        var publicId = url.parse(obj.req.url).pathname.substr(11);
        db.con.query("SELECT publicID, username, email, lastLogin, created, role FROM users WHERE publicId=?;", publicId, (err, res) => {
            if (err) {
                console.log("Error while requesting entity with the public id " + publicId);
                db.internalError(err, obj.res);
                return;
            }
            if (res.length == 1) {
                db.con.query("SELECT name, description FROM roles WHERE id=?", res[0].role, (err, result) => {
                    if (err) {
                        console.log("Error while mapping role for requested entity with the public id " + publicId + "\n" + JSON.stringify(err));
                        db.internalError(err, obj.res);
                        return;
                    }
                    res[0].role = result[0];
                    obj.res.end(JSON.stringify(res));
                });
            } else {
                obj.res.statusCode = 404;
                obj.res.statusCode = "Not found!";
                obj.res.end("The publicId is not in use!");
            }
        });
    }, (code, message) => {
        obj.res.statusCode = code;
        obj.res.statusMessage = message;
        obj.res.end();
    }, obj.res)) ;
});

server.on("updateUserByUUID", obj => { // ADMIN: update user by UUID
    // update user data by UUID if the requesting user is admin
    if (obj.req.headers['access-token'] === undefined) {
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
        obj.res.end();
        return;
    }
    var publicId = url.parse(obj.req.url).pathname.substr(11);

    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
        obj.res.end();
        return;
    }

    var username = data.username;
    var password = data.password;
    var email = data.email;

    if (username != undefined && !validate.checkUsername(username = username.trim().toLowerCase())) {
        db.unprocessable("Username not long enough!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmail(email = email.trim().toLowerCase())) {
        db.unprocessable("Email not specified!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmailFormat(email)) {
        db.unprocessable("Invalid email!", obj.res);
        return;
    }

    if (password != undefined && !validate.checkPassword(password)) {
        db.unprocessable("The password has to be at least 8 characters long!");
        return;
    }
    db.isAdmin(obj.req.headers['access-token'], () => {
        db.con.query("SELECT id FROM users WHERE publicId=?;", publicId, (err, res) => {
            if (err) {
                console.log("Error while selecting publicId!");
                db.internalError(err, obj.res);
                return;
            }
            if (res.length === 1) {
                var errorMessage = [];
                if (password != undefined) {
                    db.con.query("UPDATE users SET password=? WHERE publicId=?;", [sha512(password).toString('hex'), publicId], (err, res) => {
                        if (err) {
                            console.log("Error while updating password!");
                            errorMessage.push("An error occured while updating the password!");
                        }
                    });
                }
                if (username != undefined) {
                    db.usernameInUse(username, () => {
                        db.con.query("UPDATE users SET username=? WHERE publicId=?", [username, publicId], (err, res) => {
                            if (err) {
                                console.log("Error while updating username!");
                                errorMessage.push("An error occured while updating the username!");
                            }
                            if (email == undefined) {
                                obj.res.end(JSON.stringify({errors: errorMessage}));
                            }
                        });
                    }, (done) => {
                        if (!done) {
                            errorMessage.push("Username already in use!");
                        }
                        if (email == undefined) {
                            obj.res.end(JSON.stringify({errors: errorMessage}));
                        }
                    }, obj.res);
                }
                if (email != undefined) {
                    db.emailInUse(email, () => {
                        db.con.query("UPDATE users SET email=? WHERE publicId=?", [email, publicId], (err, res) => {
                            if (err) {
                                console.log(err);
                                errorMessage.push("An error occured while updating the email!");
                            }
                            obj.res.end(JSON.stringify({errors: errorMessage}));
                        });
                    }, (done) => {
                        if (!done) {
                            errorMessage.push("Email already in use!");
                        }
                        obj.res.end(JSON.stringify({errors: errorMessage}));
                    }, obj.res);
                }
            } else {
                // this publicId is not in use
                obj.res.statusCode = 404;
                obj.res.statusMessage = "Not found!";
                obj.res.end("The publicId is not in use!");
            }
        });
    }, (status, message) => {
        obj.res.statusCode = status;
        obj.res.statusMessage = message;
        obj.res.end();
    }, obj.res);
});

server.on("deleteUserByUUID", obj => {
    // ADMIN: delete user by UUIDs
    if (obj.req.headers['access-token'] === undefined) {
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad request!";
        obj.res.end();
        return;
    }
    db.isAdmin(obj.req.headers['access-token'], () => {
        var publicId = url.parse(obj.req.url).pathname.substr(11);
        db.con.query("SELECT id FROM users WHERE publicId=?;", publicId, (err, res) => {
            if (err) {
                console.log("An error occured while selecting publicId!");
                db.internalError(err, obj.res);
                return;
            }
            if (res.length == 0) {
                obj.res.statusCode = 404;
                obj.res.statusMessage = "Not found!";
                obj.res.end();
            } else {
                db.con.query("DELETE FROM users WHERE publicId=?", publicId, (err, res) => {
                    if (err) {
                        console.log("An error occured while deleting user!");
                        db.internalError(err, obj.res);
                        return;
                    }
                    obj.end("Deleted user successfully!");
                })
            }
        });
    }, (code, message) => {
        obj.res.statusCode = code;
        obj.res.statusMessage = message;
        obj.res.end();
    }, obj.res);
});

server.on("update", obj => {
    // updates the user account of the requesting user
    if (obj.req.headers['access-token'] === undefined) {
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
        obj.res.end();
        return;
    }

    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad Request!";
        obj.res.end();
        return;
    }

    var username = data.username;
    var password = data.password;
    var email = data.email;

    if (username != undefined && !validate.checkUsername(username = username.trim().toLowerCase())) {
        db.unprocessable("Username not long enough!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmail(email = email.trim().toLowerCase())) {
        db.unprocessable("Email not specified!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmailFormat(email)) {
        db.unprocessable("Invalid email!", obj.res);
        return;
    }

    if (password != undefined && !validate.checkPassword(password)) {
        db.unprocessable("The password has to be at least 8 characters long!");
        return;
    }
    db.con.query("SELECT user FROM tokens WHERE token=?;", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            console.log("Error while selecting token!");
            db.internalError(err, obj.res);
            return;
        }
        if (res.length === 1) {
            var errorMessage = [];
            if (password != undefined) {
                db.con.query("UPDATE users SET password=? WHERE id=?;", [sha512(password).toString('hex'), res[0].user], (err, res) => {
                    if (err) {
                        console.log("Error while updating password!");
                        errorMessage.push("An error occured while updating the password!");
                    }
                });
            }
            if (username != undefined) {
                db.usernameInUse(username, () => {
                    db.con.query("UPDATE users SET username=? WHERE id=?", [username, res[0].user], (err, res) => {
                        if (err) {
                            console.log("Error while updating username!");
                            errorMessage.push("An error occured while updating the username!");
                        }
                        if (email == undefined) {
                            obj.res.end(JSON.stringify({errors: errorMessage}));
                        }
                    });
                }, (done) => {
                    if (!done) {
                        errorMessage.push("Username already in use!");
                    }
                    if (email == undefined) {
                        obj.res.end(JSON.stringify({errors: errorMessage}));
                    }
                }, obj.res);
            }
            if (email != undefined) {
                db.emailInUse(email, () => {
                    db.con.query("UPDATE users SET email=? WHERE id=?", [email, res[0].user], (err, res) => {
                        if (err) {
                            console.log(err);
                            errorMessage.push("An error occured while updating the email!");
                        }
                        obj.res.end(JSON.stringify({errors: errorMessage}));
                    });
                }, (done) => {
                    if (!done) {
                        errorMessage.push("Email already in use!");
                    }
                    obj.res.end(JSON.stringify({errors: errorMessage}));
                }, obj.res);
            }
        } else {
            // this token is not in use
            obj.res.statusCode = 404;
            obj.res.statusMessage = "Not found!";
            obj.res.end("Token is not in use!");
        }
    });
});

server.on("delete", obj => {
    // deletes the user account of the requesting user
    if (obj.req.headers['access-token'] === undefined) {
        obj.res.statusCode = 400;
        obj.res.statusMessage = "Bad request!"
        obj.res.end("Token not specified!");
        return;
    }
    db.con.query("SELECT user FROM tokens WHERE token=?", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            console.log("Error while selecting token!");
            db.internalError(err, obj.res);
            return;
        }
        if (res.length === 0) {
            obj.res.statusCode = 404;
            obj.res.statusMessage = "Not found!";
            obj.res.end("Token not in use!");
        } else {
            db.con.query("DELETE FROM users WHERE id=?", res[0].user, (err, res) => {
                if (err) {
                    console.log("Error while deleting user!");
                    db.internalError(err, obj.res);
                    return;
                }
                obj.res.end("Deleted user successfully!");
            });
        }
    });
});