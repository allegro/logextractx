#!/usr/bin/env python
""" just minimal app for demonstration of capabilities of tox """
import flask

from logextractx.flask import init_logctx
from logextractx.middleware import getLogger


app = flask.Flask(__name__)
app.secret_key = "don't tell anyone"
init_logctx(app)


@app.route("/foo", methods=["GET"])
def foo_endpoint():
    """ just some endpoint """
    logger = getLogger("foo_endpoint")
    logger.extra["some_extra"] = "1"
    logger.info("some message logged in foo_endpoint")

    return flask.jsonify({'bar': "BAR"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1090)

