from pyquery import PyQuery as pq
from urlparse import urlsplit

def add_section_links(content, theme, resource_fetcher, log):
    """
    Add top level class links and logos for the different sections (workspace and portal).
    """
    host_url = urlsplit(log.theme_url)
    if theme("#portaltab-").html() is not None:
        home_tab_value = str(theme("#portaltab-").html())
    else:
        home_tab_value = str(content("#portaltab-").html())

    if 'workspace' in  home_tab_value:
        theme('#portal-logo img').attr('src', host_url[0] + '://' +  host_url[1] +'/++resource++portal/logo-workspace.png')        
        theme('#portal-logo img').attr('width', '803px')
        theme('#portal-logo img').attr('height', '60px')
        theme('body').addClass('template-workspace')
    else:
        theme('body').addClass('template-portal')

