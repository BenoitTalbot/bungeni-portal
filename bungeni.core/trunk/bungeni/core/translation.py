from bungeni.core.i18n import  _
from ore.alchemist import Session
from zope.security.proxy import removeSecurityProxy
from bungeni.core.interfaces import IVersionable
from bungeni.models.interfaces import IVersion

def get_language_by_name(name):
    return dict(get_all_languages())[name]

def get_default_language():
    return "en"

def get_language(context):
    return "en"

def get_all_languages():
    return (
        ('en', _(u"English")),
        ('fr', _(u"French")),
        ('sw', _(u"Swahili")),
        )
def get_available_translations(context):
    context = removeSecurityProxy(context)
    assert IVersionable.providedBy(context)
    
    model = context.versions.domain_model

    session = Session()
    query = session.query(model).filter(context.versions.subset_query).\
            distinct().values('language', 'version_id')

    return dict(query)

def is_translation(context):
    return IVersion.providedBy(context) and \
           context.status in (u"draft-translation",)
