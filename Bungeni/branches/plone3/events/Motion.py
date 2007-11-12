# -*- coding: utf-8 -*-
#
# File: Motion.py
#
# Copyright (c) 2007 by []
# Generator: ArchGenXML Version 2.0-beta4
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
from zope.interface import implements
import interfaces
from Products.Bungeni.events.ParliamentaryEvent import ParliamentaryEvent
from Products.AuditTrail.interfaces.IAuditable import IAuditable
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Relations.field import RelationField
from Products.Bungeni.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    RelationField(
        name='secondedBy',
        widget=ReferenceWidget(
            label='Secondedby',
            label_msgid='Bungeni_label_secondedBy',
            i18n_domain='Bungeni',
        ),
        multiValued=0,
        relationship='Motion_MemberOfParliament'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Motion_schema = BaseFolderSchema.copy() + \
    getattr(ParliamentaryEvent, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Motion(BrowserDefaultMixin, BaseFolder, ParliamentaryEvent):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IMotion, IAuditable)

    meta_type = 'Motion'
    _at_rename_after_creation = True

    schema = Motion_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Motion, PROJECTNAME)
# end of class Motion

##code-section module-footer #fill in your manual code here
##/code-section module-footer



