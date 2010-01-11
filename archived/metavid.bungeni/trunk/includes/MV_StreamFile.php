<?php
/*
 * MV_StreamFiles.php Created on Sep 25, 2007
 * 
 * All Metavid Wiki code is Released Under the GPL2
 * for more info visit http:/metavid.ucsc.edu/code
 * 
 * @author Michael Dale
 * @email dale@ucsc.edu
 * @url http://metavid.ucsc.edu
 */
 if ( !defined( 'MEDIAWIKI' ) )  die( 1 );
 
 /*
  * MvStreamFile handles the mapping of path types to urls & 
  * active record style management of the mv_stream_files table
  */
 
 class MV_StreamFile{
 	var $stream_id='';
 	var $base_offset='';//base offset from the stream  date_start_time
 	var $duration='';	//duration of clip.
 	var $file_desc_msg='';
 	var $path_type ='';
 	var $id = '';
 	var $path='';
 	var $_parent_stream=null;
 	
 	//@@todo this should not be hard coded... read the header of the file? or extend path_type 
 	var $msg_content_type_lookup = array(
 		'ao_file_256Kb_MPEG4'	=>'video/mp4',
 		'ao_file_64Kb_MPEG4'	=>'video/mp4',
 		'ao_file_flash_flv'		=>'video/x-flv',
 		'ao_file_MPEG1'			=>'video/mpeg',
 		'ao_file_MPEG2'			=>'video/mpeg-2',
 		'mv_ogg_high_quality'	=>'video/ogg',
 		'mv_ogg_low_quality'	=>'video/ogg'
 	);
 	function __construct(&$parent_stream, $initRow=''){
 		$this->_parent_stream =& $parent_stream;
 		//no init val.. populate from db 		 	
 		if($this->_parent_stream && $initRow==''){
 			$this->getStreamFileDB();
 		}else{		 
 			//populate from the initRow obj
			if (is_object($initRow))
				$initRow = get_object_vars($initRow);
			if (is_array($initRow)) {
				$this->updateValues($initRow);				
			}
 		}
 	}
 	function getNameKey(){
 		return $this->file_desc_msg;
 	}
 	function getContentType(){
 		if(isset($this->msg_content_type_lookup[$this->file_desc_msg])){
 			return $this->msg_content_type_lookup[$this->file_desc_msg];
 		}
 		//default content type? 
 		return 'application/octet-stream';
 	}
 	function updateValues($initRow){
		foreach ($initRow as $key => $val) {			
			//make sure the key exist and is not private
			if (isset ($this-> $key) && $key[0] != '_') {
				$this->$key = $val;
			}
		}
 	}
 	function deleteStreamFileDB(){
 		global $mvStreamFilesTable;
 		$dbw = & wfGetDB(DB_WRITE);
 		$dbw->delete($mvStreamFilesTable, array('file_id'=>$this->id));
 		//$sql = 'UPDATE '.$mvStreamFilesTable.' SET stream_id=-1 WHERE id='.$this->id;
 		//$dbw->query($sql);
 		
 	}
 	function writeStreamFileDB(){
 		global $mvMediaFilesTable,$mvStreamFilesTable;
 		$dbw = & wfGetDB(DB_WRITE); 	
 		if($this->id==''){
				$dbw->insert($mvMediaFilesTable, array(
				'base_offset'=>$this->base_offset,
				'duration'=>$this->duration,
				'file_desc_msg'=>$this->file_desc_msg,
				'path_type'=>$this->path_type,
				'path'=>$this->path
				), __METHOD__);
				$result = $dbw->query("SELECT LAST_INSERT_ID() AS id");
				$row = $dbw->fetchObject($result);
				$id = $row->id;
				$dbw->insert($mvStreamFilesTable, array('file_id'=>$id,
				'stream_id'=>$this->stream_id
				), __METHOD__);
				//$result = $dbw->query("SELECT LAST_INSERT_ID() AS id");
				//$row = $dbw->fetchObject($result);
				//$this->id = $row->id;
				
				
				
 		}else{
 			//update: 
 			$dbw->update($mvMediaFilesTable, array(				
				'base_offset'=>$this->base_offset,
				'duration'=>$this->duration,
				'file_desc_msg'=>$this->file_desc_msg,
				'path_type'=>$this->path_type,
				'path'=>$this->path
			), array('id'=>$this->id), __METHOD__);
 		}
 	}
 	function getStreamFileDB($quality=null){
		global $mvDefaultVideoQualityKey, $mvMediaFilesTable, $mvStreamFilesTable;
		if($quality==null)$quality=$mvDefaultVideoQualityKey;
		$dbr = & wfGetDB(DB_READ);
		$query = "SELECT * FROM `$mvMediaFilesTable` INNER JOIN `$mvStreamFilesTable` ON $mvMediaFilesTable.id = $mvStreamFilesTable.file_id AND $mvStreamFilesTable.stream_id=".$this->_parent_stream->getStreamId()." AND $mvMediaFilesTable.file_desc_msg=\"$quality\"";
		//$result  = $dbr->select($dbr->tableName($mvStreamFilesTable), '*', array('stream_id'=>$this->stream_id));
		//$row = $dbr->fetchObject($result);
		//$this->id = $row->file_id;
		
		//$result = $dbr->select($dbr->tableName($mvMediaFilesTable), array('path'), array (			
		//	'id' => $this->id,
		//	'file_desc_msg'=>$quality
		//));
		$result = $dbr->query($query);
		
		$row  =$dbr->fetchObject($result);
		if($row){
			$ary = get_object_vars($row);
			foreach($ary as $k=>$v){
				$this->$k=$v;
			}	
		}	
	}
	//@@todo as mentioned before we should better integrate with medaiWikis commons file system
	//returns the local path (if the video file is local) if not return null 
	function getLocalPath($quality=null){
		global $mvLocalVideoLoc,$mvDefaultVideoQualityKey;
		if($quality==null)$quality=$mvDefaultVideoQualityKey;
		
		if(!is_dir($mvLocalVideoLoc))return null;		
		if(!is_file($mvLocalVideoLoc . $this->_parent_stream->getStreamName() ))return null;
		//all looks good return: 		
		return $mvLocalVideoLoc . $this->_parent_stream->getStreamName();		
	}
 	/*
 	 * returns the path with {sn} replaced with stream name if present
 	 */
 	function getPath(){
 		return $this->path;
 		//return str_replace('{sn}',$this->_parent_stream->name, $this->path);
 	}
 	function getPathType(){
 		return $this->path_type;
 	}
 	function getFullURL(){
 		//@@todo check on path if local 
 		return $this->getPath();
 	}
 	function get_desc(){
 		return wfMsg( $this->file_desc_msg);
 	}
 }
?>
