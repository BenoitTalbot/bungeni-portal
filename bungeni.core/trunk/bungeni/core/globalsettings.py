#!/usr/bin/env python
# encoding: utf-8
"""
global settings
"""

#XXX For the time being for test purposes everything is hardcoded here.
#this is to be moved into the DB

import sqlalchemy.sql.expression as sql
from ore.alchemist import Session

import bungeni.core.domain as domain
import bungeni.core.schema as schema
from bungeni.core.i18n import _

import datetime




                


def getCurrentParliamentId(date = None):
    """
    returns the current parliament_id for a given date
    or for the current if the date is not given
    """
    def getFilter(date):
        return sql.or_(
            sql.between(date, schema.groups.c.start_date, schema.groups.c.end_date),
            sql.and_( schema.groups.c.start_date <= date, schema.groups.c.end_date == None)
            )
    
    if not date:
        date = datetime.date.today()
    session = Session() 
    query = session.query(domain.Parliament).filter(getFilter(date))   
    result = None
    try:
        result = query.one()
    except:
        pass #XXX raise( _(u"inconsistent data: none or more than one parliament found for this date"))       
    if result:        
        return result.parliament_id
        

    
def getSpeakersOfficeEmail():
    """
    return the official email address 
    of the speakers office
    """
    return "speakers.office@parliament.gov.ke"
    
def getSpeakersOfficeRecieveNotification():
    """
    returns true if the Speakers office wants to be alerted by mail
    whenever a bill, motion, question is submitted 
    """
    return True   
            
def getClerksOfficeEmail():        
    """
    return the official email address 
    of the clerks office
    """
    return "clerks.office@parliament.gov.ke"
    
def getClerksOfficeRecieveNotification():
    """
    returns true if the clerks office wants to be alerted by mail
    whenever a bill, motion, question is submitted 
    """
    return True                
    
    
def getAdministratorsEmail():
    """
    email of the site admin
    """
    return "webmaster@parliament.gov.ke"        
        
        
def getDaysToDeferAdmissibleQuestions():
    """
    time after which admissible questions are automatically deferred
    """        
    return datetime.timedelta(10)    
    
def getDaysToNotifyMinistriesQuestionsPendingResponse():
    """
    timeframe after which the clerksoffice and the ministry is alerted that
    questions that are pending response are not yet answered
    """    
    return datetime.timedelta(1)  
  
def getQuestionSubmissionAllowed():
    return True
    
def getMaxQuestionsPerSitting():
    return 3
        
def getMaxQuestionsByMpPerSitting():
    return 1
    
def getNoOfDaysBeforeQuestionSchedule():
    return 3
        
def getWeekendDays():
    """
    (0 is Monday, 6 is Sunday)
    """
    return [5,6]

def getFirstDayOfWeek():
    """
    (0 is Monday, 6 is Sunday)
    """
    return 0        
    
    
def getPloneMenuUrl():
    """
    URL at which the plone menu is returned as a json string
    """    
    return "http://192.168.0.14:40000/bungeni-public/sjMenuItems"
    
