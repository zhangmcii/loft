import logging

from flask_sqlalchemy import record_queries
from flask import current_app
from . import api


@api.after_app_request
def after_request(response):
    for query in record_queries.get_recorded_queries():
        if query.duration >= current_app.config["FLASKY_SLOW_DB_QUERY_TIME"]:
            print("发现慢查询")
            logging.warning(
                "慢查询: %s\n参数: %s\n时长: %fs\n"
                % (query.statement, query.parameters, query.duration)
            )
    return response
