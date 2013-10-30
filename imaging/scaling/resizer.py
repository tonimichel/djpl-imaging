from subprocess import Popen, PIPE
from django.utils.encoding import smart_str, DEFAULT_LOCALE_ENCODING
import os.path
from django.conf import settings
from django.core.files.images import get_image_dimensions

class ExecutionError(Exception):
    """
    Error during the execution of an external process    
    """
    def __init__(self, msg, *args, **kws):
        Exception.__init__(self, msg, *args, **kws)

def execute(cmd, args):
    """
    executes external process *cmd* with args *args*.
    """
    args.insert(0, cmd)
    args = map(smart_str, args)
    p = Popen(args, shell=False, stderr=PIPE, stdout=PIPE)
    
    #TODO there are saner ways to do this
    retcode = p.wait()
    if retcode != 0:
        raise ExecutionError(p.stderr.read().decode(DEFAULT_LOCALE_ENCODING))
    return p.stdout.read().decode(DEFAULT_LOCALE_ENCODING)

def convert(args):
    """
    calls imagemagick's convert with the specified arguments
    """
    #return execute('C:\ImageMagick-6.6.3-Q16\convert.exe', args)
    return execute('convert', args)


def create_equal_height_thumb(src, dest, width, height):
    img_format = 'x' + str(height)
    args = [src, '-thumbnail', img_format, dest]
    return convert(args)

def create_equal_width_thumb(src, dest, width, height):
    img_format = str(width) + 'x'
    args = [src, '-thumbnail', img_format,  dest]
    return convert(args)

def create_exact_size_thumb(src, dest, width, height):
    img_format = str(width) + 'x' + str(height)
    args = [src, '-thumbnail', img_format + '^', '-gravity', 'center', '-background', 'transparent' ,'-extent', img_format, dest]
    return convert(args)
    

def create_thumb(prefix, resize_func, original, width, height):
    src = original.filename
    basename = os.path.basename(src)
    dirname = os.path.dirname(src)
    tpath = '%s_%d_%d' % (prefix, width, height)
    dest = os.path.join(
        dirname,
        tpath,
        basename
    )
    execute('mkdir', ['-p', os.path.dirname(dest)])
    resize_func(src, dest, width, height)
    width, height = get_image_dimensions(dest)
    descriptor = dict(
        name=dest,
        url=original.url[len(settings.MEDIA_URL):-len(basename)] + tpath + '/' + basename,
        height=height,
        width=width,
    )
    return descriptor

def exact_width(original, width, height):
    return create_thumb('exw', create_equal_width_thumb, original, width, height)

def exact_height(original, width, height):
    return create_thumb('exh', create_equal_height_thumb, original, width, height)

def exact(original, width, height):
    return create_thumb('ex', create_exact_size_thumb, original, width, height)
    
    
    
    
    
    
    
    
