from decouple import config
from flask import jsonify

from config import create_app
from db import db


environment = config("DEV_ENVIRONMENT")
app = create_app(environment)


@app.teardown_request
def commit_on_teardown(exception=None):

    if exception is None:
        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            return (
                jsonify({
                    "Error": "An error occurred while saving data. Try again later"
                }),
                500
            )
    else:
        
        db.session.rollback()
        return (
            jsonify({
                "Error": "An unexpected error occurred. Please, contact support if the issue persists"
            }),
            500
        )

@app.teardown_appcontext
def shutdown_session(response, exception=None):

    db.session.remove()
    return response


app.run()
