from pyquery import PyQuery as pq
from urlparse import urlsplit

def workspace_add(content, theme, resource_fetcher, log, workspace_id):
    """Get the workspace content from plone using the hidden id from bungeni
    """
    workspace_item = theme('dl.workspace-tab dd#fieldset-display-form-workspace div.workspace-content')
    
    workspace_content_id = theme(workspace_id).val()
    try:
        host_url = urlsplit(log.theme_url)
        workspace_url = pq(url=host_url[0] + '://' +  host_url[1]+ "/" + workspace_content_id)
        workspace_content = workspace_url('#portal-column-content').html()
        workspace_item.append(workspace_content)
    except:
        pass


def rewrite_links(content, theme, resource_fetcher, log):
    """Fix links in folders that have been set up to act as root nodes.
    Relative links can end up with the root folder entry repeated twice.
    Remove one entry if necessary.    
    """
    link_values = ['business', 'calendar']
    content_items = {'#portal-breadcrumbs':'id', '.contentActions':'class'}

    for link_value in link_values:
        for content_item in content_items:
            content_node = theme(content_item)
            content_value = theme(content_item).html()
            if link_value + '/' + link_value +'/' in (str(content_value)):
                new_content = content_value.replace('/'+link_value+'/'+link_value, '/'+link_value)
                #print new_content
                print content_items[content_item]
                content_node.replaceWith('<div ' + content_items[content_item] +'="' + content_item[1:] +'">' + new_content + '</div>')


def drop_contentActions(content, theme, resource_fetcher, log):
    """If the user is anonymous drop the 'contentActions' bar.
    """
    content_item = pq(theme("#portal-column-content"))
    print content_item
    if not pq(theme("#portal-personaltools")).filter('#user-name'):
        content_item.remove(".contentActions")
        
    
