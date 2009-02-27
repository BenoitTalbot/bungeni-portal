#
# File: catalog.py
#
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#


import zope.interface

import transaction

from StringIO import StringIO

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCTextIndex.Lexicon import CaseNormalizer
from Products.ZCTextIndex.Lexicon import Splitter
from Products.ZCTextIndex.Lexicon import StopWordRemover
from Products.ZCTextIndex.ZCTextIndex import PLexicon

from Products.CMFCore.utils import SimpleRecord
from Products.CMFCore import utils as cmfutils

import interfaces

def setup_catalog(context):
    portal = context.getSite()

    catalog_name = 'marginalia_catalog'
    try:
        catalog = cmfutils.getToolByName(portal, catalog_name)
    except AttributeError:
        # register catalog
        catalog = ZCatalog(catalog_name, u'Marginalia catalog', None, portal)
        portal._setObject(catalog_name, catalog)
            
    # add indexes and columns
    plaintext_extra = SimpleRecord(lexicon_id='plaintext_lexicon',
                                   index_type='Okapi BM25 Rank')

    indexes = catalog.indexes()
    columns = catalog.schema()

    # install lexicon
    _id = 'plaintext_lexicon'
    if not hasattr(catalog, _id):
        lexicon = PLexicon(
            _id, '', Splitter(), CaseNormalizer(), StopWordRemover())
        catalog._setObject(_id, lexicon)

        for indexName, indexType, extra in (
            ('edit_type', 'FieldIndex', None),
            ('note', 'ZCTextIndex', plaintext_extra),
            ('link_title', 'FieldIndex', None)):      
            
            if indexName not in indexes:
                catalog.addIndex(indexName, indexType, extra=extra)
