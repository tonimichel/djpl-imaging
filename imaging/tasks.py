from ape import tasks
import os
import os.path
import subprocess
import glob

    
def refine_install_dependencies(original):
    '''
    Add install_pycopg2 to post_install_container.
    '''
    def install():
        original()
        tasks.install_imaging()
    return install
    

def sys_py(cmd):
    p = subprocess.Popen(
        cmd,
        shell=True, 
        executable='/bin/bash', 
        stdout=subprocess.PIPE
    )
    r = p.communicate()[0]
    if type(r) == str:
        r = r.replace('\n', '')
    return r
    
    
@tasks.register
def install_imaging():
    '''
    Installs python imaging container-level venv.
    '''
    sitepackages = glob.glob('%s/_lib/venv/lib/*/site-packages' % os.environ['CONTAINER_DIR'])[0]
    try:
        import PIL, _imaging
        print '...skipping:PIL is already installed'
        return
    except ImportError:
        print '... installing PIL'
    
    pildir = sys_py('/usr/bin/python -c "import PIL; print PIL.__file__"')
    
    if not (pildir) :
        print 'ERROR: Please install python-imaging first: sudo apt-get install imagemagick python-imaging python-dev libjpeg62 libjpeg62-dev zlib1g-dev; Make sure ape is not activated;'
        return
    
    pildir = os.path.dirname(pildir)

    imaging = sys_py('/usr/bin/python -c "from PIL import _imaging; import os; print os.path.abspath(_imaging.__file__)"')
    if not (imaging) :
        print 'ERROR: imaging not found; aborting'
        return
    
    os.system('ln -s %s %s' % (imaging, sitepackages))
    os.system('ln -s %s %s;' % (pildir, sitepackages))
    
    print '*** Successfully installed python imaging'
    
    
    
