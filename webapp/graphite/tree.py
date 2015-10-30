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
        node_names = path.split('.')
        if node_names[-1] == '*':
            node_names.pop()
        log.info("PATH: " + str(node_names))
        current_branches = [self.api.branch()]
        depth = 0
        leaves = []
        for node_name in node_names:
            log.info("Node: " + str(node_name))
            log.info("Cur branch: " + str(current_branches))
            next_branch_ids = []
            depth += 1
            # leaves should be at the end of the path
            leaves = []
            for current_branch in current_branches:
                for branch in current_branch['branches'] or []:
                    if node_name == '*' or self._branch_current_node_name(branch) == node_name:
                        next_branch_ids.append(branch['branchId'])
                for leaf in current_branch['leaves'] or []:
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
                        "metric_path": ".".join(
                            node_names + [self._branch_current_node_name(branch)]),
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
            last_token = path.rsplit('.', 1)[-1]
            if last_token and leaf['displayName'] != last_token:
                continue
            result.append(
                {
                    "metric_path": leaf["metric"],
                    "isLeaf": True
                }
            )
        return result
