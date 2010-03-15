from zope import component
from zope.security.proxy import removeSecurityProxy

from ore.alchemist import Session
from plone.i18n.locales.interfaces import ILanguageAvailability

from bungeni.core.interfaces import IVersionable
from bungeni.models.interfaces import IVersion
from bungeni.core.i18n import _

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from zope.publisher.browser import BrowserLanguages

class BrowserFormLanguages(BrowserLanguages):

    def getPreferredLanguages(self):
        langs = super(BrowserFormLanguages, self).getPreferredLanguages()
        form_lang = self.request.getCookies().get("I18N_LANGUAGES")
        if form_lang is not None:
            langs.insert(0, form_lang)
        return langs


class LanguageVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        languages = get_all_languages()
        items = [(l, languages[l].get('name', l)) for l in languages]
        items.sort(key=lambda language: language[1])
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)

language_vocabulary_factory = LanguageVocabulary()

def get_language_by_name(name):
    return dict(get_all_languages())[name]

def get_default_language():
    return "en"

def get_language(context):
    return context.language

def get_all_languages(filter=('en', 'fr', 'sw', 'pt')):
    """Build a list of all languages.

    To-do: the result of this method should be cached indefinitely.
    """
    
    availability = component.getUtility(ILanguageAvailability)
    languages = {}
    _languages = availability.getLanguages()

    for name in filter:
        languages[name] = _languages[name]

    return languages

def get_available_translations(context):
    context = removeSecurityProxy(context)
    #assert IVersionable.providedBy(context)
    
    
    if IVersionable.providedBy(context):
        model = context.versions.domain_model
        session = Session()
        query = session.query(model).filter(context.versions.subset_query).\
                distinct().values('language', 'version_id')

        return dict(query)
    else:
        return {'language':'', 'version_id':''}       

def is_translation(context):
    return IVersion.providedBy(context) and \
           context.status in (u"draft-translation",)
