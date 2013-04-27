Introduction
============

Simple buildout recipe that generated three commands *push a jenkins job*, *pull a jenkins job* and *trigger build on jenkins job*.

Recipe enables developer to sync configuration on Jenkins with buildout configuration.

Workflow to be used with the recipe:

- create and configure a job through the web
- run pull jenkins job
- later, make more changes the job through the web
- run pull jenkins job and use your SCM to diff the config
- (optional) push configuration to any other server or use it as restore
- (optional) trigger build, because you are too lazy to wait n minutes for cronjob

Supported options
=================

The recipe supports the following options:

hostname (required)
    Hostname of the Jenkins instance.

jobname (required)
    Name of the Jenkins job.

jobconfig (default: jenkins_config.xml)
    Name for XML configuration file for the Jenkins job, relative to buildout directory.

username (required)
    Jenkins username

password (required)
    Jenkins password

port (default: 80)
    Jenkins port

github_username
    Github username

github_password
    Github password

github_project
    Github Project name. e.g. 'plone.app.discussion'

github_hook_url
    Github hook url. e.g. 'https://api.github.com/repos/plone/Products.CMFPlone/hooks'


Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = jenkins-job
    ...
    ... [jenkins-job]
    ... recipe = collective.recipe.jenkinsjob
    ... hostname = %(hostname)s
    ... jobname = %(jobname)s
    ... jobconfig = %(jobconfig)s
    ... username = %(username)s
    ... password = %(password)s
    ... """ % {
    ...     'hostname' : 'jenkins.plone.org',
    ...     'jobname' : 'Plone42',
    ...     'jobconfig': 'plone.xml',
    ...     'username': 'chuck',
    ...     'password': 'norris'})

Running the buildout gives us::

    >>> buildout_output_lower = system(buildout).lower()
    >>> "installing jenkins-job" in buildout_output_lower
    True
    >>> "generated script" in buildout_output_lower
    True
    >>> "bin/jenkins-job-push" in buildout_output_lower
    True
    >>> "bin/jenkins-job-pull" in buildout_output_lower
    True
    >>> "bin/jenkins-job-trigger-build" in buildout_output_lower
    True


Github Post-commit hook example
===============================

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = jenkins-job
    ...
    ... [jenkins-job]
    ... recipe = collective.recipe.jenkinsjob
    ... hostname = %(hostname)s
    ... jobname = %(jobname)s
    ... jobconfig = %(jobconfig)s
    ... username = %(username)s
    ... password = %(password)s
    ... github_username = %(github_username)s
    ... github_password = %(github_password)s
    ... github_project = %(github_project)s
    ... """ % {
    ...     'hostname' : 'jenkins.plone.org',
    ...     'jobname' : 'Plone42',
    ...     'jobconfig': 'plone.xml',
    ...     'username': 'chuck',
    ...     'password': 'norris',
    ...     'github_username': 'john',
    ...     'github_password': 'doe',
    ...     'github_project': 'plone.app.discussion'
    ... })

Running the buildout gives us::

    >>> buildout_output_lower = system(buildout).lower()
    >>> "installing jenkins-job" in buildout_output_lower
    True
    >>> "generated script" in buildout_output_lower
    True
    >>> "bin/jenkins-job-push" in buildout_output_lower
    True
    >>> "bin/jenkins-job-pull" in buildout_output_lower
    True
    >>> "bin/jenkins-job-trigger-build" in buildout_output_lower
    True

Alternatively, instead of providing a github_project param you can provide a
github_hook_url:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = jenkins-job
    ...
    ... [jenkins-job]
    ... recipe = collective.recipe.jenkinsjob
    ... hostname = %(hostname)s
    ... jobname = %(jobname)s
    ... jobconfig = %(jobconfig)s
    ... username = %(username)s
    ... password = %(password)s
    ... github_username = %(github_username)s
    ... github_password = %(github_password)s
    ... github_hook_url = %(github_hook_url)s
    ... """ % {
    ...     'hostname' : 'jenkins.plone.org',
    ...     'jobname' : 'Plone42',
    ...     'jobconfig': 'plone.xml',
    ...     'username': 'chuck',
    ...     'password': 'norris',
    ...     'github_username': 'john',
    ...     'github_password': 'doe',
    ...     'github_hook_url': 'https://api.github.com/repos/plone/Products.CMFPlone/hooks'
    ... })
