import flask
from peewee import *

from . import database

blueprint = flask.Blueprint("tasks", __name__)


def get_tasks_count():
    tasks_count = database.Task.select().where((database.Task.status == "pending") |
                                               (database.Task.status == "running")).count()
    return tasks_count


@blueprint.route('/tasks', methods=['GET'])
def get_tasks():
    """List all tasks.py."""
    tasks = database.Task.select()
    return flask.jsonify({
        "data": [task.to_response(flask.request.base_url) for task in tasks]
    })


@blueprint.route('/tasks/<int:id>', methods=['DELETE'])
def del_tasks(id):
    """List all tasks.py."""
    try:

        task = database.Task.select().where(database.Task.id == id).get()
        task.delete_instance()
        task.save()
    except database.Task.DoesNotExist:
        return flask.jsonify({"error": "not exist"}), 400
    return flask.jsonify({"description": "successful operation"}), 204


@blueprint.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    """List all tasks.py."""
    try:
        task = database.Task.select().where(database.Task.id == id).get()
    except database.Task.DoesNotExist:
        return flask.jsonify({"error": "not exist"}), 400
    return flask.jsonify({
        "data": task.to_response(flask.request.base_url)
    })


@blueprint.route('/tasks/<int:id>/logs', methods=['GET'])
def get_logs(id):
    try:
        task = database.Task.select().where(database.Task.id == id).get()
    except database.Task.DoesNotExist:
        return flask.jsonify({"error": "not exist"}), 400
    response = flask.make_response(task.logs, 200)
    response.mimetype = "text/plain"
    return response


@blueprint.route('/tasks/', methods=['POST'])
def create_task():
    if get_tasks_count() >= 100:
        return flask.jsonify({"error": "limit tasks exceeded, delete any existing tasks before"}), 400
    """Create the new docker task"""
    if "data" not in flask.request.json:
        return flask.jsonify({"error": "data is required"}), 400

    if "attributes" not in flask.request.json["data"]:
        return flask.jsonify({"error": "data.attributes is required"}), 400

    if "title" not in flask.request.json["data"]["attributes"]:
        return flask.jsonify({"error": "data.attributes.title is required"}), 400

    task = database.Task.create(
        title=flask.request.json["data"]["attributes"]["title"],
        command=flask.request.json["data"]["attributes"]["command"],
        image=flask.request.json["data"]["attributes"]["image"],
        description=flask.request.json["data"]["attributes"]["description"],
    )

    return flask.jsonify({"data": task.to_response(flask.request.base_url)}), 201
