__doc__ = """

Contains implementation of OpenTSDB tree which helps browse metrics space.

"""

from graphite.logger import log


class OpenTSDBMetricsMeta(object):
    """Metrics tree."""
    def __init__(self, api):
        self.api = api

    def _branch_current_node_name(self, branch):
        return branch['path'][str(branch['depth'])]

    def find(self, path):
        """path is a dot separated metric prefix.

        Returns children of a node with given path.

        """
        log.info("OpenTSDBMetricsMeta.find(%s)" % path)
        node_names = filter(None, path.split('.'))
        current_branch = self.api.branch()
        depth = 0
        for node_name in node_names:
            branches = current_branch['branches'] or []
            next_branch_id = None
            depth += 1
            for branch in branches:
                if self._branch_current_node_name(branch) == node_name:
                    next_branch_id = branch['branchId']
                    break
            if next_branch_id is None:
                return []
            current_branch = self.api.branch(branch_id=next_branch_id)
        log.info("CURRENT BRANCH: %s" % current_branch)
        result = []
        for branch in current_branch['branches'] or []:
            result.append(
                {
                    "metric_path": ".".join(node_names + [self._branch_current_node_name(branch)]),
                    "isLeaf": False
                }
            )
        for leave in current_branch['leaves'] or []:
            result.append(
                {
                    "metric_path": leave['metric'],
                    "isLeaf": True
                }
            )
        return result
