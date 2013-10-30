import re
import logging
import imageresizer
from django.utils.safestring import mark_safe
from mptt.managers import TreeManager
from django.conf import settings
import os.path

logger = logging.getLogger(__name__)

class FolderManager(TreeManager):
    
    def create_at_toplevel(self, name):
        from filemanager.models import Folder, get_root_folder
        root = get_root_folder()
        return self.insert_node(
            Folder(name = name),
            root,
            save=True,
        )

VARIANT_REGEX = re.compile(r'^(?:(.*)_)(\d+)x(\d+)$')

RESIZERS = dict(
    exact = imageresizer.exact,
    exact_height = imageresizer.exact_height,
    exact_width = imageresizer.exact_width,
)


class OriginalImage(object):

    def __init__(self, model):
        self.model = model

    @property
    def url(self):
        the_url = self.model.image_obj.url
        if '://' in the_url:
            the_url = the_url.split('://')[1]
            the_url = the_url[the_url.index('/'):]
        return the_url

    @property
    def filename(self):
        return os.path.join(settings.MEDIA_ROOT, self.model.image_obj.name)

    @property
    def height(self):
        try:
            return self.model.image_obj.height
        except IOError:
            logger.exception('Error while getting image height')
            return 0

    @property
    def width(self):
        try:
            return self.model.image_obj.width
        except IOError:
            logger.exception('Error while getting image height')
            return 0

    @property
    def alt(self):
        return self.model.alt_text

    @property
    def title(self):
        return self.model.title

    def __unicode__(self):
        img = '<img src="%s" width="%s" height="%s" alt="%s" title="%s" />' % (
            self.url,
            str(self.width),
            str(self.height),
            self.alt or '',
            self.title or '',
        )
        return mark_safe(img)

class ImageVariant(object):

    def __init__(self, model, descriptor):
        self.descriptor = descriptor
        self.model = model

    @property
    def url(self):
        the_url = self.descriptor['url']
        if '://' in the_url:
            the_url = the_url.split('://')[1]
            the_url = the_url[the_url.index('/'):]
        return the_url

    @property
    def filename(self):
        return settings.MEDIA_ROOT + self.descriptor['name']

    @property
    def height(self):
        return self.descriptor['height']

    @property
    def width(self):
        return self.descriptor['width']

    @property
    def alt(self):
        return self.model.alt_text

    @property
    def title(self):
        return self.model.title

    def __unicode__(self):
        img = '<img src="%s%s" width="%s" height="%s" alt="%s" title="%s" />' % (
            settings.MEDIA_URL,
            self.url,
            str(self.width),
            str(self.height),
            self.alt or '',
            self.title or '',
        )
        return mark_safe(img)

class ImageVariantManager(object):

    def __init__(self, model):
        self.model = model
        self.original = OriginalImage(self.model)

    def __getattr__(self, name):
        if not 'image_cache' in self.model.jsondata:
            self.model.jsondata['image_cache'] = dict()
        imagecache = self.model.jsondata['image_cache']
        if name in imagecache:
            variant = ImageVariant(self.model, imagecache[name])
            if os.path.isfile(variant.filename):
                return variant
        match = VARIANT_REGEX.match(name)
        if match:
            width = int(match.group(2))
            height = int(match.group(3))
            mode = match.group(1)
            if not mode in RESIZERS:
                raise AttributeError

            resizer = RESIZERS[mode]
            try:
                descriptor = resizer(self.original, width, height)
                if descriptor['name'].startswith(settings.MEDIA_ROOT):
                    descriptor['name'] = descriptor['name'][len(settings.MEDIA_ROOT):]
                imagecache[name] = descriptor
                self.model.save()
            except imageresizer.ExecutionError as ex:
                descriptor = dict(name="404", url="404", width=width, height=height)
                logger.warn('Error while resizing image: ' + repr(ex))
            return ImageVariant(self.model, descriptor)

        raise AttributeError
