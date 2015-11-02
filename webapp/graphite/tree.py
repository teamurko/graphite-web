__doc__ = """

Contains implementation of OpenTSDB tree which helps browse metrics space.

"""

import re

from graphite.logger import log

ANY_PATTERN = '.*'


class OpenTSDBMetricsMeta(object):
    """Metrics tree."""
    def __init__(self, api):
        self.api = api

    def _branch_current_path(self, branch):
        path = branch['path']
        path = '.'.join([v for _, v in sorted(path.items())])
        return path

    def _branch_current_node_name(self, branch):
        return branch['path'][str(branch['depth'])]

    def find(self, path):
        """path is a dot separated metric prefix.

        Returns children of a node with given path.

        """
        log.info("OpenTSDBMetricsMeta.find(%s)" % path)
        node_names = []
        for part in path.split('.'):
            part = part.replace('*', ANY_PATTERN)
            part = re.sub(
                r'{([^{]*)}',
                lambda x: "(%s)" % '|'.join(("^%s$" % y for y in x.groups()[0].split(','))),
                part,
            )
            node_names.append(part)

        if node_names[-1] == ANY_PATTERN:
            node_names.pop()

        query_part_regexps = []
        for part in node_names:
            query_part_regexps.append(re.compile(part))
        log.info("PATH: " + str(node_names))
        current_branches = [self.api.branch()]
        depth = 0
        leaves = []
        for node_regexp in query_part_regexps:
            log.info("Node: " + str(node_regexp))
            log.info("Cur branch: " + str(current_branches))
            next_branch_ids = []
            depth += 1
            # leaves should be at the end of the path
            leaves = []
            for current_branch in current_branches:
                for branch in current_branch['branches'] or []:
                    if node_regexp.match(self._branch_current_node_name(branch)):
                        next_branch_ids.append(branch['branchId'])
                for leaf in current_branch['leaves'] or []:
                    if node_regexp.match(leaf['displayName']):
                        leaves.append(leaf)
            log.info("next_branch_ids: " + str(next_branch_ids))

            current_branches = []

            for next_branch_id in next_branch_ids:
                current_branches.append(self.api.branch(branch_id=next_branch_id))

        log.info("CURRENT BRANCHES: %s" % current_branches)
        result = []
        for current_branch in current_branches:
            for branch in current_branch['branches'] or []:
                result.append(
                    {
                        "metric_path": self._branch_current_path(branch),
                        "isLeaf": False
                    }
                )
            for leaf in current_branch['leaves'] or []:
                result.append(
                    {
                        "metric_path": leaf['metric'],
                        "isLeaf": True
                    }
                )
        for leaf in leaves:
            log.info("LEAF: " + str(leaf))
            result.append(
                {
                    "metric_path": leaf["metric"],
                    "isLeaf": True
                }
            )
        return result
