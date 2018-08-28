"use strict";
const server = require("./main.js");
const db = require("./databaseFunctions.js");
const sha512 = require('sha512');
const validate = require('./validation.js');
const url = require('url');
const uuidv4 = require('uuid/v4');
const responder = require('./response.js');

server.on("getAll", obj => { // GET /api/users - ADMIN: get data of all users
    db.isAdmin(obj.req.headers["access-token"],
        () => {
            // is admin
            db.con.query("SELECT username, publicID, email, lastLogin, created, role FROM users;",
                (err, res) => {
                    if (err) {
                        db.internalError(err, obj.res);
                        return;
                    }
                    for (let i = 0; i < res.length; i++) {
                        db.con.query("SELECT name, description FROM roles WHERE id=?;", res[i].role,
                            (error, result) => {
                                if (err) {
                                    db.internalError(error, obj.res);
                                    return;
                                }
                                res[i].role = result[0];
                                if (i === res.length - 1) {
                                    responder.respond(obj.res, 200, "OK", undefined, JSON.stringify((res)));
                                }
                            }
                        );
                    }
                }
            );
        },
        (code, message, customMessage) => {
            //is not admin
            responder.respond(obj.res, code, message, customMessage);
        },
        obj.res
    );
});

server.on("register", obj => { // register a new user
    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        responder.respond(obj.res, 400, "Bad request!", "Invalid JSON format!");
    }

    if (!validate.checkUsername(data.username)) {
        // username length not ok
        responder.unprocessable("Username not long enough!", obj.res);
        return;
    }

    if (!validate.checkEmail(data.email)) {
        // email length not ok
        responder.unprocessable("Email not specified!", obj.res);
        return;
    }

    if (!validate.checkEmailFormat(data.email)) {
        // email format not ok
        responder.unprocessable("Invalid email!", obj.res);
        return;
    }

    if (!validate.checkPassword(data.password)) {
        //password not long enough
        responder.unprocessable("The password has to be at least 8 characters long!", obj.res);
        return;
    }

    db.usernameInUse(data.username.trim(),
        () => {
            //username not used
            db.emailInUse(data.email.trim(),
                () => {
                    //create Account
                    var insertionData = {
                        publicID: generateUUID4(),
                        username: data.username.trim().toLowerCase(),
                        email: data.email.trim().toLowerCase(),
                        password: sha512(data.password).toString('hex')
                    };
                    db.con.query("INSERT INTO users SET ?", insertionData,
                        (err, res) => {
                            if (err) {
                                db.internalError(err, obj.res);
                                return;
                            }
                            console.log("User " + data.username.trim() + " created successfully!");
                            responder.respond(obj.res, 201, "Created!", undefined, "User successfully created!");
                        }
                    );
                },
                done => {
                    // email in use
                    if (!done) {
                        responder.unprocessable("Email already in use!", obj.res);
                    }
                },
                obj.res
            );
        },
        done => {
            //username in use
            if (!done) {
                responder.unprocessable("The username is already in use!", obj.res);
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
                db.internalError(err, obj.res);
                return;
            }
            if (res.length == 1) {
                db.con.query("SELECT name, description FROM roles WHERE id=?", res[0].role, (err, result) => {
                    if (err) {
                        db.internalError(err, obj.res);
                        return;
                    }
                    res[0].role = result[0];
                    responder.respond(obj.res, 200, "Ok!", undefined, JSON.stringify(res));
                });
            } else {
                responder.respond(obj.res, 404, "Not found!", "The publicId is not in use!");
            }
        });
    }, (code, message, customMessage) => {
        responder.respond(obj.res, code, message, customMessage);
    }, obj.res)) ;
});

server.on("updateUserByUUID", obj => { // ADMIN: update user by UUID
    // update user data by UUID if the requesting user is admin
    var publicId = url.parse(obj.req.url).pathname.substr(11);

    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        responder.respond(obj.res, 400, "Bad request!", "Invalid JSON format!");
        return;
    }

    var username = data.username;
    var password = data.password;
    var email = data.email;

    if (username != undefined && !validate.checkUsername(username = username.trim().toLowerCase())) {
        responder.unprocessable("Username not long enough!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmail(email = email.trim().toLowerCase())) {
        responder.unprocessable("Email not specified!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmailFormat(email)) {
        responder.unprocessable("Invalid email!", obj.res);
        return;
    }

    if (password != undefined && !validate.checkPassword(password)) {
        responder.unprocessable("The password has to be at least 8 characters long!");
        return;
    }
    db.isAdmin(obj.req.headers['access-token'], () => {
        db.con.query("SELECT id FROM users WHERE publicId=?;", publicId, (err, res) => {
            if (err) {
                db.internalError(err, obj.res);
                return;
            }
            if (res.length === 1) {
                var errorMessage = [];
                var successMessage = [];
                if (password != undefined) {
                    db.con.query("UPDATE users SET password=? WHERE publicId=?;", [sha512(password).toString('hex'), publicId], (err, res) => {
                        if (err) {
                            errorMessage.push("An error occured while updating the password!");
                        } else {
                            successMessage.push("Password updated successfully!");
                        }
                    });
                }
                if (username != undefined) {
                    db.usernameInUse(username, () => {
                        db.con.query("UPDATE users SET username=? WHERE publicId=?", [username, publicId], (err, res) => {
                            if (err) {
                                errorMessage.push("An error occured while updating the username!");
                            } else {
                                successMessage.push("Username updated successfully!");
                            }
                            if (email == undefined) {
                                responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                            }
                        });
                    }, (done) => {
                        if (!done) {
                            errorMessage.push("Username already in use!");
                        }
                        if (email == undefined) {
                            responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                        }
                    }, obj.res);
                }
                if (email != undefined) {
                    db.emailInUse(email, () => {
                        db.con.query("UPDATE users SET email=? WHERE publicId=?", [email, publicId], (err, res) => {
                            if (err) {
                                errorMessage.push("An error occured while updating the email!");
                            } else {
                                successMessage.push("Email updated successfully!");
                            }
                            responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                        });
                    }, (done) => {
                        if (!done) {
                            errorMessage.push("Email already in use!");
                        }
                        responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                    }, obj.res);
                }
            } else {
                // this publicId is not in use
                responder.respond(obj.res, 404, "Not found!", "The publicId is not in use!");
            }
        });
    }, (status, message, customMessage) => {
        responder.respond(obj.res, status, message, customMessage);
    }, obj.res);
});

server.on("deleteUserByUUID", obj => {
    // ADMIN: delete user by UUIDs
    db.isAdmin(obj.req.headers['access-token'], () => {
        var publicId = url.parse(obj.req.url).pathname.substr(11);
        db.con.query("SELECT id FROM users WHERE publicId=?;", publicId, (err, res) => {
            if (err) {
                db.internalError(err, obj.res);
                return;
            }
            if (res.length == 0) {
                responder.respond(obj.res, 404, "Not found!", "The publicId is not in use!");
            } else {
                db.con.query("DELETE FROM users WHERE publicId=?", publicId, (err, res) => {
                    if (err) {
                        db.internalError(err, obj.res);
                        return;
                    }
                    responder.respond(obj.res, 200, "Ok!", undefined, "Deleted user successfully!")
                })
            }
        });
    }, (code, message, costumMessage) => {
        responder.respond(obj.res, code, message, costumMessage);
    }, obj.res);
});

server.on("update", obj => {
    // updates the user account of the requesting user
    if (obj.req.headers['access-token'] === undefined) {
        responder.respond(obj.res, 400, "Bad request!", "Token not specified!");
        return;
    }

    try {
        var data = JSON.parse(obj.data);
    } catch (err) {
        // no JSON object
        responder.respond(obj.res, 400, "Bad request!", "Invalid JSON format!");
        return;
    }

    var username = data.username;
    var password = data.password;
    var email = data.email;

    if (username != undefined && !validate.checkUsername(username = username.trim().toLowerCase())) {
        responder.unprocessable("Username not long enough!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmail(email = email.trim().toLowerCase())) {
        responder.unprocessable("Email not specified!", obj.res);
        return;
    }

    if (email != undefined && !validate.checkEmailFormat(email)) {
        responder.unprocessable("Invalid email!", obj.res);
        return;
    }

    if (password != undefined && !validate.checkPassword(password)) {
        responder.unprocessable("The password has to be at least 8 characters long!");
        return;
    }
    db.con.query("SELECT user FROM tokens WHERE token=?;", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            db.internalError(err, obj.res);
            return;
        }
        if (res.length === 1) {
            var errorMessage = [];
            var successMessage = [];
            if (password != undefined) {
                db.con.query("UPDATE users SET password=? WHERE id=?;", [sha512(password).toString('hex'), res[0].user], (err, res) => {
                    if (err) {
                        errorMessage.push("An error occured while updating the password!");
                    } else {
                        successMessage.push("Password updated successfully!");
                    }
                });
            }
            if (username != undefined) {
                db.usernameInUse(username, () => {
                    db.con.query("UPDATE users SET username=? WHERE id=?", [username, res[0].user], (err, res) => {
                        if (err) {
                            errorMessage.push("An error occured while updating the username!");
                        } else {
                            successMessage.push("Username updated successfully!");
                        }
                        if (email == undefined) {
                            responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                        }
                    });
                }, (done) => {
                    if (!done) {
                        errorMessage.push("Username already in use!");
                    }
                    if (email == undefined) {
                        responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                    }
                }, obj.res);
            }
            if (email != undefined) {
                db.emailInUse(email, () => {
                    db.con.query("UPDATE users SET email=? WHERE id=?", [email, res[0].user], (err, res) => {
                        if (err) {
                            console.log(err);
                            errorMessage.push("An error occured while updating the email!");
                        } else {
                            successMessage.push("Email updated successfully!");
                        }
                        responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                    });
                }, (done) => {
                    if (!done) {
                        errorMessage.push("Email already in use!");
                    }
                    responder.respond(obj.res, errorMessage.length == 0 ? 200 : 422, errorMessage.length == 0 ? "OK" : "Unprocessable entity!", errorMessage.length == 0 ? undefined : errorMessage, successMessage.length == 0 ? undefined : successMessage);
                }, obj.res);
            }
        } else {
            // this token is not in use
            responder.respond(obj.res, 404, "Not found!", "Token not in use!");
        }
    });
});

server.on("delete", obj => {
    // deletes the user account of the requesting user
    if (obj.req.headers['access-token'] === undefined) {
        responder.respond(obj.res, 400, "Bad request!", "Token not specified!");
        return;
    }
    db.con.query("SELECT user FROM tokens WHERE token=?", obj.req.headers['access-token'], (err, res) => {
        if (err) {
            db.internalError(err, obj.res);
            return;
        }
        if (res.length === 0) {
            responder.respond(obj.res, 404, "Not found!", "Token not in use!");
        } else {
            db.con.query("DELETE FROM users WHERE id=?", res[0].user, (err, res) => {
                if (err) {
                    db.internalError(err, obj.res);
                    return;
                }
                responder.respond(obj.res, 404, "Ok!", undefined, "Deleted user successfully!");
            });
        }
    });
});