__author__ = 'Solomon S. Gifford <sgifford@blackmesh.com>'

import gitlab
import logging

try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

logger = logging.getLogger(__name__)

class GitlabWrapper(gitlab.Gitlab):

    def __init__(self, *args, **kwargs):
        super(GitlabWrapper, self).__init__(*args, **kwargs)
        try:
            current_user = self.currentuser()
            logger.debug("Current git user is %s" % current_user['username'])
        except Exception, e:
            logger.error("Unable to log into git %s" % e)
            raise Exception("Unable to log into git")

    #gname = None is really gname = "any"
    def findproject(self, pname, gname=None, user=False):
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
