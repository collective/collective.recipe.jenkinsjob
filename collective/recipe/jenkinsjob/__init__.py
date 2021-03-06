# -*- coding: utf-8 -*-
"""Recipe Jenkinsjob"""
import os
from shutil import copyfile

import jenkins
import zc.recipe.egg
from zc.buildout import UserError
from github import create_hook


class Recipe(object):
    """Recipe to configure Jenkins CI jobs.
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = zc.recipe.egg.Scripts(
            buildout,
            self.options['recipe'],
            options)

        # Check required options
        required_options = [
            'hostname',
            'jobname',
            'username',
            'password',
            'jobconfig'
        ]
        for required_option in required_options:
            if required_option not in self.options:
                raise UserError(
                    'Please provide a "%s" in your jenkins section "%s"' % (
                    required_option,
                    self.options['recipe']))

        # Set default options
        self.options.setdefault('port', '80')
        self.options.setdefault('jobconfig', 'jenkins_config.xml')
        self.options['config'] = os.path.join(
            self.buildout['buildout']['directory'],
            self.options['jobconfig'])

        # Figure out default output file
        plone_jenkins = os.path.join(
            self.buildout['buildout']['parts-directory'], __name__)
        if not os.path.exists(plone_jenkins):
            os.makedirs(plone_jenkins)

        # What files are tracked by this recipe
        self.files = [plone_jenkins,
            os.path.join(
                self.buildout['buildout']['bin-directory'], self.name)]

    def install(self):
        """Installer"""
        self.install_scripts()
        self.install_github_hook()

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return self.files

    def update(self):
        """Updater"""
        self.install()

    def install_scripts(self):
        """Install a jenkins-job script in the bin directory.
        """
        zc.buildout.easy_install.scripts(
            [(
                self.name + '-push',
                'collective.recipe.jenkinsjob',
                'push_jenkins_job'
            )],
            self.egg.working_set()[1],
            self.buildout[self.buildout['buildout']['python']]['executable'],
            self.buildout['buildout']['bin-directory'],
            arguments=self.options.__repr__(),
        )
        zc.buildout.easy_install.scripts(
            [(
                self.name + "-pull",
                'collective.recipe.jenkinsjob',
                'pull_jenkins_job'
            )],
            self.egg.working_set()[1],
            self.buildout[self.buildout['buildout']['python']]['executable'],
            self.buildout['buildout']['bin-directory'],
            arguments=self.options.__repr__(),
        )
        zc.buildout.easy_install.scripts(
            [(
                self.name + "-trigger-build",
                'collective.recipe.jenkinsjob',
                'trigger_build_jenkins'
            )],
            self.egg.working_set()[1],
            self.buildout[self.buildout['buildout']['python']]['executable'],
            self.buildout['buildout']['bin-directory'],
            arguments=self.options.__repr__(),
        )

    def install_github_hook(self):
        has_gh_username = 'github_username' in self.options
        has_gh_password = 'github_password' in self.options
        github_project = None
        if 'github_project' in self.options:
            github_project = self.options['github_project']
        github_hook_url = None
        if 'github_hook_url' in self.options:
            github_hook_url = self.options['github_hook_url']

        if has_gh_username and has_gh_password and (github_hook_url or github_project):
            create_hook(
                self.options['hostname'],
                self.options['username'],
                self.options['password'],
                self.options['github_username'],
                self.options['github_password'],
                self.options['jobname'],
                github_project=github_project,
                github_hook_url=github_hook_url,
            )

def _connect(options):
    """Connect to a Jenkins CI server.
    """
    return jenkins.Jenkins(
        options['hostname'],
        options['username'],
        options['password'])


def _write_configuration(config, filename):
    # Backup existing config if it exists
    if os.path.exists(filename):
        print("Create Jenkins job backup at %s.bak" % filename)
        copyfile(filename, "%s.bak" % filename)
    # Write config to file
    print("Write job %s" % filename)
    fileObj = open(filename, "w")
    fileObj.write(config)
    fileObj.close()


def trigger_build_jenkins(options):
    """Trigger a build for a job on Jenkins CI server.
    """
    jenkins_server = _connect(options)
    jenkins_jobname = options['jobname']
    if jenkins_server.job_exists(jenkins_jobname):
        print(
            "Build Jenkins job %s" %
            jenkins_server.get_job_info(jenkins_jobname)['url'])
        try:
            jenkins_server.build_job(jenkins_jobname)
        except jenkins.JenkinsException, e:
            print e


def pull_jenkins_job(options):
    """Pull a remote job from a Jenkins server.
    """
    jenkins_server = _connect(options)
    print("Pull Jenkins job %s" % options['jobname'])
    job_config = jenkins_server.get_job_config(options['jobname'])
    if job_config:
        _write_configuration(job_config, options['config'])
    else:
        print("Jenkins job '%s' seems not to exist on '%s'." % (
            options['jobname'],
            options['hostname']))
        print("Make sure the job exists and is accessible by user '%s'." %
            options['username'])


def push_jenkins_job(options):
    """Push a job to the Jenkins CI server.
    """
    # Variables
    jenkins_url = options['hostname']
    jenkins_username = options['username']
    jenkins_password = options['password']
    jenkins_jobname = options['jobname']
    jenkins_config = open(options['config']).read()

    # Connect to Jenkins CI server
    jenkins_server = jenkins.Jenkins(
        jenkins_url,
        jenkins_username,
        jenkins_password)

    # Create Jenkins job
    if jenkins_server.job_exists(jenkins_jobname):
        print(
            "Reconfig Job %s" %
            jenkins_server.get_job_info(jenkins_jobname)['url'])
        try:
            jenkins_server.reconfig_job(jenkins_jobname, jenkins_config)
        except jenkins.JenkinsException, e:
            print e
    else:
        jenkins_server.create_job(jenkins_jobname, jenkins_config)
        print(
            "Create Job %s" %
            jenkins_server.get_job_info(jenkins_jobname)['url'])
