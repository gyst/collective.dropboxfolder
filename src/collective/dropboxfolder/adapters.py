
from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility

from zope.annotation import IAnnotations
from plone.i18n.normalizer.interfaces import IURLNormalizer 

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import createContentInContainer

from collective.dropboxfolder.interfaces import IDropboxSyncProcessor
from collective.dropboxfolder.interfaces import IDropboxSync
from collective.dropboxfolder.interfaces import IDropboxMetadata
from collective.dropboxfolder.content.dropbox_folder import IDropboxFolder
from collective.dropboxfolder.content.config import DROPBOX_FOLDER_TYPE
from collective.dropboxfolder.content.config import DROPBOX_FILE_TYPE

METADATA_KEY = "collective.dropboxfolder.metadata"


class DropboxMetadata(object):
    
    implements(IDropboxMetadata)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def get(self):
        annotations = IAnnotations(self.context)
        return annotations.get(METADATA_KEY, None)

    def set(self, value):
        assert(isinstance(value,dict))
        annotations = IAnnotations(self.context)
        annotations[METADATA_KEY] = value


class DropboxSyncProcessor(object):
    
    implements(IDropboxSyncProcessor)
    adapts(IDropboxFolder)

    def __init__(self, context):
        self.context = context

    def sync(self):
        connector = getUtility(IDropboxSync)

        normalize = getUtility(IURLNormalizer).normalize
        container = self.context

        delta = connector.delta()

        entries = delta.get('entries', [])
        for entry in entries:
            path = [x for x in entry[0].split('/') if x]
            folders = path[:-1]
            filename = path[-1]

            container_fti = container.getTypeInfo()
        
            if container_fti is not None and not container_fti.allowType(DROPBOX_FILE_TYPE):
                raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FILE_TYPE,))
            
            ob = createContentInContainer(container,
                                          DROPBOX_FILE_TYPE,
                                          checkConstraints=False,
                                          id=normalize(filename),
                                          )

            IDropboxMetadata(ob).set(entry[1])



