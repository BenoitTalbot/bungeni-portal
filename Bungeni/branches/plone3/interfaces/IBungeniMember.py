# -*- coding: utf-8 -*-
#
# File: IBungeniMember.py
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


##code-section module-header #fill in your manual code here
##/code-section module-header


from zope.interface import implements

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin


from zope import interface

class IBungeniMember(interface.Interface):
    ''' '''

    ##code-section class-header_IBungeniMember #fill in your manual code here
    ##/code-section class-header_IBungeniMember




    def getFullname():
       """


    def setFullname():
       """


##code-section module-footer #fill in your manual code here
##/code-section module-footer



