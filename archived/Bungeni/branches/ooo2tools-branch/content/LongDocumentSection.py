# -*- coding: utf-8 -*-
#
# File: LongDocumentSection.py
#
# Copyright (c) 2007 by []
# Generator: ArchGenXML Version 1.6.0-beta-svn
#            http://plone.org/products/archgenxml
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

__author__ = """Jean Jordaan <jean.jordaan@gmail.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope import interface
from Products.PloneHelpCenter.content.ReferenceManualSection import HelpCenterReferenceManualSection
from Products.Bungeni.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

LongDocumentSection_schema = BaseFolderSchema.copy() + \
    getattr(HelpCenterReferenceManualSection, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class LongDocumentSection(BaseFolder, HelpCenterReferenceManualSection):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),) + (getattr(HelpCenterReferenceManualSection,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Document Section'

    meta_type = 'LongDocumentSection'
    portal_type = 'LongDocumentSection'
    allowed_content_types = ['LongDocumentPage', 'ATFile', 'ATImage', 'Take']
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'LongDocumentSection.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "A section of a longer document."
    typeDescMsgId = 'description_edit_longdocumentsection'

    _at_rename_after_creation = True

    schema = LongDocumentSection_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(LongDocumentSection, PROJECTNAME)
# end of class LongDocumentSection

##code-section module-footer #fill in your manual code here
##/code-section module-footer



