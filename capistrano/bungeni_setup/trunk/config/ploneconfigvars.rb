#### CONFIG VARIABLE SETTING ####

set :user24_python_home, "#{user_python24_runtime}"
## user python is used to run bungeni in the user context -- this is a pre-requisite
#was "/home/bungeni/apps/python"
set :user24_python, "#{user24_python_home}/bin/python"

#was set :deploy_to, "/home/bungeni/bungeni_deploy/#{application}"
set :plone_buildout_dir, "#{buildout_dir}/plone"
set :plone_local_buildout_config_file , "buildout_plone_local.cfg"
set :plone_respository,  "https://bungeni-portal.googlecode.com/svn/plone.buildout/trunk"


