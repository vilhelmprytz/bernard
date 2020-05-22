####################################################################
#                                                                  #
# Bernard                                                          #
# Copyright (C) 2020, Vilhelm Prytz, <vilhelm@prytznet.se>, et al. #
#                                                                  #
# Licensed under the terms of the MIT license, see LICENSE.        #
# https://github.com/vilhelmprytz/bernard                          #
#                                                                  #
####################################################################

from flask import Flask, render_template

# imports
from version import version, commit_hash
from time import strftime

app = Flask(__name__)

# inject global variables
@app.context_processor
def inject_global_variables():
    return dict(
        version=version,
        commit_hash=commit_hash[0:7],
        generation_time=strftime("%Y-%m-%d %H:%M:%S"),
    )


# errorhandlers
@app.errorhandler(400)
def error_400(e):
    return (
        render_template("error.html", error_code=400, error_message=e.description),
        400,
    )


@app.errorhandler(404)
def error_404(e):
    return (
        render_template("error.html", error_code=404, error_message=e.description),
        404,
    )


@app.errorhandler(405)
def error_405(e):
    return (
        render_template("error.html", error_code=405, error_message=e.description),
        405,
    )


@app.errorhandler(429)
def error_429(e):
    return (
        render_template("error.html", error_code=429, error_message=e.description),
        429,
    )


@app.errorhandler(500)
def error_500(e):
    return (
        render_template("error.html", error_code=500, error_message=e.description),
        500,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
