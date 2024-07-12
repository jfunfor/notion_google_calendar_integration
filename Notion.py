import os
from notion_client import Client
from datetime import datetime, timezone, timedelta


class Notion(object):

    #  connect to notion api
    def __init__(self, notion_token):
        self.service = Client(auth=notion_token)

    #  handle case when there is no time in start time event property
    def handle_start_time(self, date):
        #  if no iso format then add hardcode clock time and convert from string to datetime
        if "T" not in date or "+" not in date:
            result_date = datetime.strptime(str(date) + f"T23:00:00.000", "%Y-%m-%dT%H:%M:%S.%f").replace(
                tzinfo=timezone(timedelta(hours=+3)))
        else:
            result_date = datetime.fromisoformat(date)
        return result_date

    #  handle case when there is no time in end time event property. Func is bound with start time iso format
    def handle_end_time(self, date, start_time, deviation_time: int):
        # if end date from notion is empty or not in iso format, assign it to start_date time + deviation_time
        if date is None or "T" not in date or "+" not in date or datetime.fromisoformat(date) == start_time:
            result_date = start_time + timedelta(minutes=deviation_time)
        else:
            result_date = datetime.fromisoformat(date)
        return result_date

    def get_query_db(self, query_template) -> list:
        # send query to notion database
        filtered_database = self.service.databases.query(**query_template)
        result_list = []
        # run through query result from notion database. Extract date, name and id only
        for object in filtered_database["results"]:
            result_list.append({})

            #  to reduce number of characters in code
            last_el = result_list[len(result_list) - 1]

            #  build result list with only required properties from notion
            last_el["name"] = object["properties"]["Name"]["title"][0]["text"]["content"]
            last_el["id"] = object["id"]
            last_el["start_date"] = self.handle_start_time(object["properties"]["Date"]["date"]["start"])
            last_el["end_date"] = self.handle_end_time(object["properties"]["Date"]["date"]["end"],
                                                       last_el["start_date"],
                                                       30)

            last_el["start_date"] = last_el["start_date"].isoformat()
            last_el["end_date"] = last_el["end_date"].isoformat()

        # got only useful data from notion database as list of objects
        return result_list
