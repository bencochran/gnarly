from __future__ import with_statement
from fabric.api import run, env, local, cd, require, abort
from fabric.contrib.files import exists

env.repository = 'git@github.com:bcochran/gnarly.git'
env.branch = 'origin/master'

## Environments

def production():
    env.hosts = ['gnarus@slice.gnar.us']
    env.deploy_to = '/home/gnarus/production'

def development():
    env.hosts = ['gnarus@slice.gnar.us']
    env.deploy_to = '/home/gnarus/development'

# Actions

def deploy():
    '''
    Deploy the code. First push our repository, then either setup the
    repository or update it.
    '''
    require('deploy_to')
    
    local("git push")
    
    if not exists(env.deploy_to):
        setup()
    else:
        update()
    cleanup()


def setup():
    '''
    Setup a fresh git-style deployment.
    '''
    require('repository')
    require('deploy_to')
    
    run('git clone %(repository)s %(deploy_to)s' % env)


def update():
    '''
    Update the deployed code
    '''
    with cd(env.deploy_to):
        run("git fetch origin; git reset --hard %(branch)s" % env)


def rollback():
    '''
    Rollback a single commit.
    '''
    if not exists(env.deploy_to):
        abort("cannot rollback if we've never deployed")
    env.branch = "HEAD^"
    update()    

def cleanup():
    # do we need this to do anything?
    pass


## Aliases
prod = production
dev = development
