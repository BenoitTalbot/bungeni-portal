=begin
Sets up the pre-requisities for DSpace 
  -- Required System libraries
  -- User JVM (instead of using the system JVM)
  -- User tomcat application server
  -- Maven
  -- Ant
  -- Downloads and installs Postgres for the current user
=end


### Defines a sequence of tasks for installing bungeni from scratch ###

#### General Build Parameter #####

=begin
 Only the following 2 parameters need to be set by the user to customize
  this installation script for different computers
=end
set :user_root, "/home/undesa/bungeni_dspace"
set :user_build_root, "#{user_root}/cap_builds"
set :user_install_root, "#{user_root}/cap_installs"

#### download URLs for components #####
### Can be set to a http / ftp url or an absolute path to the file on the computer
### Edit these as desired ############
set :dl_cache_folder, "/home/undesa/cache"
set :java6_download_url, "#{dl_cache_folder}/jdk-6u14-ea-bin-b06-linux-i586-06_may_2009.bin" # "http://www.java.net/download/jdk6/6u14/promoted/b06/binaries/jdk-6u14-ea-bin-b06-linux-i586-06_may_2009.bin"
set :tomcat_download_url, "#{dl_cache_folder}/apache-tomcat-5.5.27.tar.gz" #"http://mirror.cinquix.com/pub/apache/tomcat/tomcat-5/v5.5.27/bin/apache-tomcat-5.5.27.tar.gz"
set :maven_download_url, "#{dl_cache_folder}/apache-maven-2.1.0-bin.tar.gz" #"http://www.apache.org/dist/maven/binaries/apache-maven-2.1.0-bin.tar.gz"
set :ant_download_url, "#{dl_cache_folder}/apache-ant-1.7.1-bin.tar.gz" #"http://archive.apache.org/dist/ant/binaries/apache-ant-1.7.1-bin.tar.gz"
set :pg_download_url, "#{dl_cache_folder}/postgresql-8.3.7.tar.gz" #"http://wwwmaster.postgresql.org/download/mirrors-ftp/source/v8.3.7/postgresql-8.3.7.tar.gz"
set :dspace_download_url, "#{dl_cache_folder}/dspace-1.5.2-release.tar.gz"

##### Component Specific Parameters ##### 

### do not edit any of these parameters (unless you know what you are doing) #### 

#### Java 6  #####
set :java6_install_binary, "jdk6.bin"
set :java6_install_dir_name, File.basename(java6_install_binary, ".bin")
set :java6_download_command, get_download_command(java6_download_url, java6_install_binary)
set :java6_home, "#{user_install_root}/#{java6_install_dir_name}"
set :java6_download_dir, "#{user_build_root}/#{java6_install_dir_name}"

#### Tomcat 5.5  #####
set :tomcat_install_archive, "tomcat.tar.gz"
set :tomcat_install_dirname, File.basename(tomcat_install_archive, ".tar.gz")
set :tomcat_download_command, get_download_command(tomcat_download_url, tomcat_install_archive)
set :tomcat_home, "#{user_install_root}/#{tomcat_install_dirname}"
set :tomcat_download_dir, "#{user_build_root}/#{tomcat_install_dirname}"
set :tomcat_server_xml, "#{tomcat_home}/conf/server.xml"
set :tomcat_users_xml, "#{tomcat_home}/conf/tomcat-users.xml"

set :tomcat_host, "localhost"
set :tomcat_port, "20000" ## do not use 9000
set :tomcat_admin_user, "admin"
set :tomcat_admin_password, "admin"


##### Maven #####
set :maven_install_archive, "maven.tar.gz"
set :maven_install_dirname, File.basename(maven_install_archive, ".tar.gz")
set :maven_download_command, get_download_command(maven_download_url, maven_install_archive)
set :maven_home, "#{user_install_root}/#{maven_install_dirname}"
set :maven_download_dir, "#{user_build_root}/#{maven_install_dirname}"

##### Ant #####
set :ant_install_archive, "ant.tar.gz"
set :ant_install_dirname, File.basename(ant_install_archive, ".tar.gz")
set :ant_download_command, get_download_command(ant_download_url, ant_install_archive)
set :ant_home, "#{user_install_root}/#{ant_install_dirname}"
set :ant_download_dir, "#{user_build_root}/#{ant_install_dirname}"

##### Postgres #####
set :pg_install_archive, "postgres.tar.gz"
set :pg_install_dirname, File.basename(pg_install_archive, ".tar.gz")
set :pg_download_command, get_download_command(pg_download_url, pg_install_archive)
set :pg_home, "#{user_install_root}/#{pg_install_dirname}"
set :pg_data, "#{pg_home}/data"
set :pg_download_dir, "#{user_build_root}/#{pg_install_dirname}"

##### DSpace #####
set :dspace_version, File.basename(dspace_download_url, "-release.tar.gz") # e.g. 'dspace-1.5.2'
set :dspace_install_archive, "dspace.tar.gz"
set :dspace_installation_name, "Bungeni Dspace"
set :dspace_install_dirname, File.basename(dspace_install_archive, ".tar.gz")
set :dspace_download_command, get_download_command(dspace_download_url, dspace_install_archive)
set :dspace_home, "#{user_install_root}/#{dspace_install_dirname}"
set :dspace_download_dir, "#{user_build_root}/#{dspace_install_dirname}"
set :dspace_config_file, "dspace.cfg.erb"
set :dspace_db_user_name, "undesa"
set :dspace_db_user_password, "undesa"
set :dspace_smtp, "localhost"
set :dspace_db_name, "dspace"
set :dspace_maven_root, "#{dspace_download_dir}/#{dspace_install_dirname}"
set :dspace_maven_target_dir, "#{dspace_maven_root}/dspace/target/#{dspace_version}-build.dir"
set :dspace_server_xml, "#{tomcat_home}/conf/server_dspace.xml"
set :dspace_tomcatusers_xml, "#{tomcat_home}/conf/tomcat-users_dspace.xml"

### DSpace Admin user ###
set :dspace_admin_email, "ashok@parliaments.info"
set :dspace_admin_fname, "ashok"
set :dspace_admin_lname, "hariharan"
set :dspace_admin_password, "password"




namespace :dspace_presetup do
	
    desc "Installs the OS prequisites for DSpace"
    task :essentials, :roles=> [:app] do
	run "echo 'Installing OS Essentials'"
	required_libs = [
			"build-essential", # for building from source
			"linux-headers-`uname -r`", # for building from source
			"openssl", # for java ssl
			"libssl-dev", # for java ssl
			"bison", # for pg
			"flex", # for pg
			"libreadline5-dev", # for pg
			"zlib1g-dev", # for pg
			"wget" # for downloading stuff 
			]
	install_cmd = "apt-get install " + required_libs * " " 	+ " -y"
	sudo install_cmd
    end

    task :init, :roles=> [:app] do 
	[
	"mkdir -p #{user_build_root}",
	"mkdir -p #{user_install_root}",
	"mkdir -p #{java6_download_dir}",
	"mkdir -p #{tomcat_download_dir}",
	"mkdir -p #{maven_download_dir}",
	"mkdir -p #{ant_download_dir}",
	"mkdir -p #{pg_download_dir}",
	"mkdir -p #{dspace_download_dir}"
	].each {|cmd| run cmd}
    end

    desc "Install java6 jvm"
    task :jvm, :roles=> [:app] do
	[
	"rm -rf #{java6_home}",
	"cd #{java6_download_dir} && #{java6_download_command} && chmod ug+x ./#{java6_install_binary}",
	"cd #{java6_download_dir} && echo y > answer.txt",
	"cd #{java6_download_dir}  && ./#{java6_install_binary} <answer.txt &>/dev/null",
	"cd #{java6_download_dir}  &&  mv ./jdk1.6* #{java6_home}"
	].each {|cmd| run cmd}
    end

    desc "Install Tomcat"
    task :tomcat, :roles=> [:app] do
	[
	"rm -rf #{tomcat_home}",
	"cd #{tomcat_download_dir} && #{tomcat_download_command}",
	"cd #{tomcat_download_dir} && mkdir ./#{tomcat_install_dirname} && tar xvzf #{tomcat_install_archive} -C ./#{tomcat_install_dirname} --strip-components=1",
	"cd #{tomcat_download_dir} &&  mv ./#{tomcat_install_dirname} #{tomcat_home}"
	].each {|cmd| run cmd}
    end
	
    desc "Install Maven"
    task :maven, :roles=> [:app] do
	[
	"rm -rf #{maven_home}",
	"cd #{maven_download_dir} && #{maven_download_command}",
	"cd #{maven_download_dir} && mkdir ./#{maven_install_dirname} && tar xvzf #{maven_install_archive} -C ./#{maven_install_dirname} --strip-components=1",
	"cd #{maven_download_dir} &&  mv ./#{maven_install_dirname} #{maven_home}"
	].each {|cmd| run cmd}
    end

    desc "Install Ant"
    task :ant, :roles=> [:app] do
	[
	"rm -rf #{ant_home}",
	"cd #{ant_download_dir} && #{ant_download_command}",
	"cd #{ant_download_dir} && mkdir ./#{ant_install_dirname} && tar xvzf #{ant_install_archive} -C ./#{ant_install_dirname} --strip-components=1",
	"cd #{ant_download_dir} &&  mv ./#{ant_install_dirname} #{ant_home}"
	].each {|cmd| run cmd}
    end
	
    desc "Install Postgres"
    task :postgres, :roles=> [:app] do
	[
	"rm -rf #{pg_home}",
	"cd #{pg_download_dir} && #{pg_download_command}",
	"cd #{pg_download_dir} && mkdir ./#{pg_install_dirname} && tar xvzf #{pg_install_archive} -C ./#{pg_install_dirname} --strip-components=1",
	"mkdir -p #{pg_home}",
	"cd #{pg_download_dir}/#{pg_install_dirname} && ./configure --prefix='#{pg_home}' && make && make install ",
	"mkdir -p #{pg_data}",
	"#{pg_home}/bin/initdb -D #{pg_data}",
	"#{pg_home}/bin/postgres -D #{pg_data} >logfile 2>&1 &",
	"sleep 6", # sleep for 6 seconds to wait for postgres to start 
	"#{pg_home}/bin/createdb test"
	].each {|cmd| run cmd}
    end

    desc "Install DSpace"
    task :dspace, :roles=> [:app] do
	[
	"rm -rf #{dspace_home}",
	"cd #{dspace_download_dir} && #{dspace_download_command}",
	"cd #{dspace_download_dir} && mkdir ./#{dspace_install_dirname} && tar xvzf #{dspace_install_archive} -C ./#{dspace_install_dirname} --strip-components=1"
	].each {|cmd| run cmd}
    end
    
end
