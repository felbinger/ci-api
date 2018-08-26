"use strict";
const http = require('http');
const url = require('url');
const EventEmitter = require('events');
const emitter = new EventEmitter();
module.exports = emitter;
const auth = require('./auth.js');
const users = require('./users.js');
const challenges = require('./challenges.js');

http.createServer((req, res) => {
    var body = "";
    req.on("data", data => {
        body += data;
    });

    req.on("end", () => {
        var path = url.parse(req.url).pathname;
        switch (path) {
            case "/api/auth":
                switch (req.method) {
                    case "GET": // get information about an account
                        emitter.emit("getUser", {
                            "res": res,
                            "req": req
                        });
                        break;
                    case "POST": // login
                        emitter.emit("login", {
                            "req": req,
                            "res": res,
                            "data": body
                        });
                        break;
                    case "DELETE": // logout
                        emitter.emit("logout", {
                            "req": req,
                            "res": res
                        });
                        break;
                    default:
                        methodNotAllowed(res);
                        break;
                }
                break;
            case "/api/users":
                switch (req.method) {
                    case "GET": // ADMIN: Get information about all users
                        emitter.emit("getAll", {
                            "req": req,
                            "res": res
                        });
                        break;
                    case "POST": // register new user
                        emitter.emit("register", {
                            "req": req,
                            "res": res,
                            "data": body
                        });
                        break;
                    default:
                        methodNotAllowed(res);
                        break;
                }
                break;
            case String(path.match(/^\/api\/users\/[A-F\d]{8}-[A-F\d]{4}-4[A-F\d]{3}-[89AB][A-F\d]{3}-[A-F\d]{12}$/i)):
                switch (req.method) {
                    case "GET": // get the data of a user by UUID
                        emitter.emit("getUserByUUID", {
                            "req": req,
                            "res": res
                        });
                        break;
                    case "PUT": // update the data of a user by UUID
                        emitter.emit("updateUserByUUID", {
                            "req": req,
                            "res": res,
                            "data": body
                        });
                        break;
                    case "DELETE": // delete user by UUID
                        emitter.emit("deleteUserByUUID", {
                            "req": req,
                            "res": res
                        });
                        break;
                    default:
                        methodNotAllowed(res);
                        break;
                }
                break;
            case "/api/users/me":
                switch (req.method) {
                    case "PUT": // update user
                        emitter.emit("update", {
                            "req": req,
                            "res": res,
                            "data": body
                        });
                        break;
                    case "DELETE": // delete user
                        emitter.emit("delete", {
                            "req": req,
                            "res": res
                        });
                        break;
                    default:
                        methodNotAllowed(res);
                        break;
                }
                break;
            default:
                res.statusCode = 404;
                res.statusMessage = "Page not found!";
                res.end();
                break;
        }
    });
}).listen(2002);

function methodNotAllowed(res) {
    res.statusCode = 405;
    res.statusMessage = "Method not allowed!";
    res.end();
}