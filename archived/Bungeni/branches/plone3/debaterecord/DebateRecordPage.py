# -*- coding: utf-8 -*-
#
# File: DebateRecordPage.py
#
# Copyright (c) 2007 by []
# Generator: ArchGenXML Version 2.0-beta5
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Jean Jordaan <jean.jordaan@gmail.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope import interface
from zope.interface import implements
import interfaces
from Products.PloneHelpCenter.content.ReferenceManualPage import HelpCenterReferenceManualPage
from Products.AuditTrail.interfaces.IAuditable import IAuditable
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Bungeni.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

DebateRecordPage_schema = BaseSchema.copy() + \
    getattr(HelpCenterReferenceManualPage, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class DebateRecordPage(BrowserDefaultMixin, BaseContent, HelpCenterReferenceManualPage):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IDebateRecordPage, IAuditable)

    meta_type = 'DebateRecordPage'
    _at_rename_after_creation = True

    schema = DebateRecordPage_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(DebateRecordPage, PROJECTNAME)
# end of class DebateRecordPage

##code-section module-footer #fill in your manual code here
##/code-section module-footer



