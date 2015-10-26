__doc__ = """

Contains adhoc wrappers and tools for working with OpenTSDB server.

"""

import httplib
import httplib2
import json


class API(object):
    def __init__(self, host_with_port):
        self.headers = {'Content-Type': 'application/json'}
        self.http = httplib2.Http()
        self.branch_url_template = "http://%s/api/tree/branch?branch={branch_id}" % host_with_port
        self.query_url = "http://%s/api/query" % host_with_port

    def branch(self, branch_id=None):
        """Requests branch meta data.

        http://opentsdb.net/docs/build/html/api_http/tree/branch.html

        """
        branch_id = branch_id or '0001'  # root branch id
        url = self.branch_url_template.format(branch_id=branch_id)
        response, content = self.http.request(url, 'GET', headers=self.headers)
        if int(response['status']) != httplib.OK:
            raise Exception("Could not read data points: %s" % repr(response))
        return json.loads(content)

    # TODO add tags and aggregators
    def query(self, metric, start_time, end_time):
        """Fetches time series data."""
        body = {
            "start": start_time,
            "end": end_time,
            "queries": [
                {
                    "aggregator": "avg",
                    "metric": metric,
                    "rate": "false",
                    "tags": None,
                    "downsample": "1m-avg"
                }
            ]
        }
        response, content = self.http.request(
            self.query_url, 'POST', headers=self.headers, body=json.dumps(body))
        if int(response['status']) != httplib.OK:
            raise Exception("Could not read data points: %s" % repr(response))
        return json.loads(content)
