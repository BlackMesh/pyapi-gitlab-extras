# -*- coding: utf-8 -*-
import gitlab
import logging

__author__ = 'Solomon S. Gifford <sgifford@blackmesh.com>'

logger = logging.getLogger(__name__)

try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    logger.error("Failed to monkey-patch urllib3 with PyOpenSSL-backed SSL support", exc_info=True)


class GitlabWrapper(gitlab.Gitlab):

    def __init__(self, *args, **kwargs):
        super(GitlabWrapper, self).__init__(*args, **kwargs)
        try:
            current_user = self.currentuser()
            logger.debug("Current git user is %s" % current_user['username'])
        except Exception, e:
            logger.error("Unable to log into git %s" % e)
            raise Exception("Unable to log into git")

    def findproject(self, pname, gname=None, user=False):
        """Attempts to find a project

        :param pname: project name
        :param gname: group name, "none" implies "any"
        :param user:
        :return: the project or False if not found
        """
        if not pname:
            logger.error('Missing project name')
            return False

        page = 1
        projects = self.getprojects(page=page, per_page=20)
        while len(projects) > 0:
            for project in projects:
                if gname is None and 'name' in project and project['name'].lower() == pname.lower():
                    return project
                elif not user and gname and project['namespace']['name'].lower() == gname.lower() and project['name'].lower() == pname.lower():
                    return project
                elif user and gname and project['namespace']['path'].lower() == gname.lower() and project['name'].lower() == pname.lower():
                    return project
            page += 1
            projects = self.getprojects(page=page, per_page=20)
        else:
            return False

    def findgroup(self, path):
        page = 1
        groups = self.getgroups(page=page, per_page=20)

        while len(groups) > 0:
            for group in groups:
                if group['path'] == path:
                    return group

            page += 1
            groups = self.getgroups(page=page, per_page=20)

        return False

    def allgroups(self):
        page = 1
        all_groups = []

        paged_groups = self.getgroups(page=page)
        all_groups += paged_groups

        while len(paged_groups) > 0:
            page += 1
            paged_groups = self.getgroups(page=page)
            all_groups += paged_groups

        return all_groups

    def deleteproject(self, project_name, group=None):
        project = self.findproject(project_name, group)
        if project:
            project_id = project['id']
            super(GitlabWrapper, self).deleteproject(project_id)
        else:
            logger.warning('Project not found to delete')
            return False

    def getbranches(self, project_id, limits=None, delimiter=","):
        """List all the branches from a project

        :param project_id: project id
        :param limits: list or comma-separated string of branches to limit
        :param delimiter: delimiter for branch limits
        :return: the branches
        """
        branches = super(GitlabWrapper, self).getbranches(project_id)
        if limits:
            if isinstance(limits, basestring):
                limits = [limit.strip() for limit in limits.split(delimiter)]
            branches = [branch for branch in branches if branch['name'] in limits]
        return branches
