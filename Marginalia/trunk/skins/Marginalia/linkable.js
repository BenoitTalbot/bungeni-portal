/*
 * linkable.js
  *
 * Marginalia has been developed with funding and support from
 * BC Campus, Simon Fraser University, and the Government of
 * Canada, and units and individuals within those organizations.
 * Many thanks to all of them.  See CREDITS.html for details.
 * Copyright (C) 2005-2007 Geoffrey Glass www.geof.net
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

AN_MAKELINKTARGET_CLASS = 'make-link-target';	// this content element's children can be made link targets by clicking
AN_LINKTARGET_CLASS = 'link-target';	// the node is the clicked target of a link
AN_FLASH_CLASS = 'flash';			// the display is flashing this node

AN_LINKING_COOKIE = 'marginalia-linking';
AN_LINKURL_COOKIE = 'marginalia-link-url';

/**
 * If the window gains focus and linking is on, enable link targets
 */
function _enableLinkTargets( )
{
	if ( readCookie( AN_LINKING_COOKIE ) )
	{
		var postElements = getChildrenByTagClass( document.documentElement, null, PM_POST_CLASS, null, _skipPostContent );
		for ( var i = 0;  i < postElements.length;  ++i )
		{
			var post = getPostMicro( postElements[ i ] );
			var content = post.getContentElement( );
			addClass( content, AN_MAKELINKTARGET_CLASS );
			content.addEventListener( 'click', _clickLinkTarget, false );
		}
	}
}


/**
 * If the window loses focus, disable link targets
 */
function _disableLinkTargets( )
{	
	var postElements = getChildrenByTagClass( document.documentElement, null, PM_POST_CLASS, null, _skipPostContent );
	for ( var i = 0;  i < postElements.length;  ++i )
	{
		var post = getPostMicro( postElements[ i ] );
		var content = post.getContentElement( );
		removeClass( content, AN_MAKELINKTARGET_CLASS );
		content.removeEventListener( 'click', _clickLinkTarget, false );
	}
	window.removeEventListener( 'blur', _disableLinkTargets, false );
}


/**
 * The user has clicked on a link target.  Update the relevant annotation with
 * the new link.
 */
function _clickLinkTarget( event )
{
	event = getEvent( event );
	stopPropagation( event );
	var target = event.target;
	var content = getParentByTagClass( target, null, PM_CONTENT_CLASS, false, null );
	
	// Need to look at parent targets until a block level element is found
	while ( 'block' != htmlDisplayModel( target.tagName ) )
		target = target.parentNode;
	
	// Calculate path to target
	var path = NodeToPath( content, target );
	var link = '' + window.location;
	if ( -1 != link.indexOf( '#' ) )
		link = link.substring( 0, link.indexOf( '#' ) );
	link = link + '#' + path;
	
	// Get the annotation
	var annotationId = readCookie( AN_LINKING_COOKIE );
	if ( null != annotationId )
	{
		// must replace ; characters in cookie
		createCookie( AN_LINKURL_COOKIE, link, 1 );

		content.removeEventListener( 'click', _clickLinkTarget, false );
		removeClass( content, AN_MAKELINKTARGET_CLASS );
		addClass( target, AN_FLASH_CLASS );
		target.flashcount = 4;
		setTimeout( _flashLinkTarget, 240 );
	}
	
	// If the link was made from this window, leave editing mode
	_disableLinkTargets( );
	_updateLinks( );
}

function _flashLinkTarget( )
{
	var target = getChildByTagClass( document.documentElement, null, AN_FLASH_CLASS, null );
	if ( target.flashcount > 0 )
	{
		if ( target.flashcount % 2 )
			removeClass( target, AN_LINKTARGET_CLASS );
		else
			addClass( target, AN_LINKTARGET_CLASS );
		target.flashcount -= 1;
		setTimeout( _flashLinkTarget, 240 );
	}
	else
	{
		removeClass( target, AN_LINKTARGET_CLASS );
		removeClass( target, AN_FLASH_CLASS );
		delete target.flashcount;
	}
}

