#!/usr/bin/env python

# find all .git directories
# take their dirname
# check remotes
# check status
# eventually we could id repos to remove because they're synced

import os, subprocess, sys, re, multiprocessing, json

class GitDir:
    def __init__(self,path,**kwargs):
        self.path = path
        self.result_queue = multiprocessing.Queue()
        # run the check in a subprocess
        self.checkproc = multiprocessing.Process(target=self.Check)
        self.checkproc.start()
    def Wait(self):
        # wait for the check to complete so they can run in parallel
        if self.checkproc.is_alive():
            self.repo_status = self.result_queue.get()
            self.checkproc.join()
    def Check(self):
       print "Proc ", os.getpid(), " Running check for ", self.path 
       # run the checks and get the results 
       self.result_queue.put( { "git status": self.GitStatus() } )
    def call(self,args):
        print "Call ", args
        proc = subprocess.Popen(args,cwd=self.path,stdout=subprocess.PIPE)
        comm = proc.communicate(None)
        return (comm, proc.returncode)
    def GitStatus(self):
        git_status = self.call(["git","status","--porcelain"])
        print git_status
        return git_status
    def Report(self):
        self.Wait()
        return self.repo_status

print "Base proc ", os.getpid()

basepath=os.environ.get("BASEPATH",".")
findproc=subprocess.Popen(["find", basepath, "-name", ".git", "-type", "d"],stdout=subprocess.PIPE)
gitdirs = []
for line in iter(findproc.stdout.readline,''):
    gd = GitDir(os.path.dirname(str.strip(line)))
    gitdirs.append(gd)
[ sys.stderr.write(json.dumps(gd.Report()) + "\n") for gd in gitdirs ]
