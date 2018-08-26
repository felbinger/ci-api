function respond(response, code, statusMessage, errors, success) {
    response.statusCode = code;
    response.message = statusMessage;
    var result = {};

    if (errors != undefined) {
        if (Array.isArray(errors)) {
            result.error = errors;
        } else {
            result.error = [errors];
        }
    } else if (code < 200 || code >= 300) {
        result.error = statusMessage;
    }

    if (success != undefined) {
        if (Array.isArray(success)) {
            result.success = success;

        } else {
            result.success = [success];
        }
    }
    response.end(JSON.stringify(result));
}

module.exports.respond = respond;

function unprocessable(error, res) {
    respond(res, 422, "Unprocessable entity!", error);
}

module.exports.unprocessable = unprocessable;