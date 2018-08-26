function respond(response, code, message) {
    console.log("die ohne message");
    response.statusCode = code;
    response.message = message;
    response.end();
}

module.exports.respond = respond;

function respond(response, code, statusMessage, message) {
    console.log("die mit message");
    response.statusCode = code;
    response.message = statusMessage;
    response.end(message);
}

module.exports.respond = respond;
