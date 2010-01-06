import sqlalchemy as rdb
from sqlalchemy.orm import mapper
from datetime import datetime
metadata = rdb.MetaData()

def make_changes_table( table, metadata ):
    """Create an object log table for an object."""
    
    table_name = table.name
    entity_name =  table_name.endswith('s') and table_name[:-1] or table_name
    
    changes_name = "%s_changes"%( entity_name )
    fk_id = "%s_id"%( entity_name )
    
    changes_table = rdb.Table(
            changes_name,
            metadata,
            rdb.Column( "change_id", rdb.Integer, primary_key=True ),
            rdb.Column( "content_id", rdb.Integer, rdb.ForeignKey( table.c[ fk_id ] ) ),
            rdb.Column( "action", rdb.Unicode(16) ),
            rdb.Column( "date",  rdb.DateTime( timezone=False ), default=datetime.now),
            rdb.Column( "description", rdb.UnicodeText),
            rdb.Column( "notes", rdb.UnicodeText),
            rdb.Column( "user_id", rdb.Unicode(32) ) # Integer, rdb.ForeignKey('users.user_id') ),
    )
    
    return changes_table
 
def make_versions_table( table, metadata, secondarytable=None ):
    """Create a versions table, requires change log table for which
    some version metadata information will be stored.
    
    A secondary table may be defined if the object mapped to this 
    table consists of a join betwee two tables   
    """
    
    table_name = table.name
    entity_name =  table_name.endswith('s') and table_name[:-1] or table_name
    
    versions_name = "%s_versions"%( entity_name )
    fk_id = "%s_id"%( entity_name )
    
    columns = [
        rdb.Column( "version_id", rdb.Integer, primary_key=True ),
        rdb.Column( "content_id", rdb.Integer, rdb.ForeignKey( table.c[ fk_id ] ) ),
        rdb.Column( "change_id", rdb.Integer, rdb.ForeignKey('%s_changes.change_id'%entity_name)),
        rdb.Column( "manual", rdb.Boolean, nullable=False, default=False),
    ]
    
    columns.extend( [ c.copy() for c in table.columns if not c.primary_key ] )
    if secondarytable:
        columns.extend( [ c.copy() for c in secondarytable.columns if not c.primary_key ] )        
    #primary = [ c.copy() for c in table.columns if c.primary_key ][0]
    #primary.primary_key = False
    #columns.insert( 2, primary )
    
    versions_table = rdb.Table(
            versions_name,
            metadata,
            *columns 
            )
            
    return versions_table

transcript_table = rdb.Table(
    "transcripts",
    metadata,
    rdb.Column('transcript_id', rdb.Integer, primary_key=True),  
    rdb.Column("person", rdb.Integer, nullable=False),
    rdb.Column("text", rdb.UnicodeText),
    rdb.Column("start_time", rdb.Unicode(80), nullable=False),
    rdb.Column("end_time", rdb.Unicode(80), nullable=False),
    #rdb.Column("sitting_id", rdb.Integer, rdb.ForeignKey('sitting_table.id')),
   )

transcript_changes = make_changes_table( transcript_table, metadata )
transcript_versions = make_versions_table( transcript_table, metadata)

sitting_table = rdb.Table(
    "Sitting",
    metadata,
    rdb.Column('sitting_id', rdb.Integer, primary_key=True), 
    )
