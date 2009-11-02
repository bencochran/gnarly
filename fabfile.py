from __future__ import with_statement
from fabric.api import run, env, local, cd


env.hosts = ['gnarus@slice.gnar.us']
env.deploy_to = '/home/gnarus/slice'
env.repository = 'git@github.com:bcochran/gnarly.git'
env.branch = 'origin/master'

def deploy():
    update()
    cleanup()

def setup():
    '''
    Setup a fresh git-style deployment.
    '''
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
    
    env.branch = "HEAD^"
    deploy()    

def cleanup():
    # do we need this?
    pass