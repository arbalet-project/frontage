# script to install easily arbalet server
# has to be execute as root
name=`whoami`

if [[ "$name" == "root" ]]; then
  echo bonjour
else
  echo au revoir
  # exit 1
fi

# Determine package manager and correct sintax from distribution name
distrib=`cat /etc/*-release | grep ^NAME | sed 's/NAME=\"\(.*\)\"/\1/'`

package_manager=pkgmanager
install_cmd=install
list_cmd=list
end_chr=""

function get_pkgmanager {
  echo "$1"
  case $1 in
    "Arch Linux" )
      package_manager=pacman
      install_cmd="-S"
      list_cmd="-Q"
      end_chr="\ "
      ;;
    "Ubuntu" )
      package_manager=apt
      install_cmd="install"
      list_cmd="list --installed"
      end_chr="/"
      ;;
  esac
}

get_pkgmanager "$distrib"

echo "You are running this script on $distrib distribution, $package_manager will be used"

# List of package to install
pkg_list="docker docker-compose ufw"
pkg_to_install=""

function to_install {
  while [[ $# -gt 0 ]]; do
    var=`$package_manager $list_cmd | grep "^$1$end_chr"`
    if [[ "$var" == "" ]]; then
      pkg_to_install="$pkg_to_install $1"
    fi
    shift
  done
}

to_install $pkg_list

# Installation of required package
if [[ "$pkg_to_install" != "" ]]; then
  echo "Packages$pkg_to_install need to be installed"
  $package_manager $install_cmd $pkg_to_install
else
  echo "All required packages are installed ==> skipping installation"
fi

# Check installation
pkg_to_install=""
to_install $pkg_list

if [[ "$pkg_to_install" != "" ]]; then
  echo "ERROR :$pkg_to_install packages are missing ==> Abort"
  exit 1
fi

# Configuration of firewall
# Range allow to pass : 192.168.0.32 to 192.168.0.127
# ufw allow proto tcp from 192.168.0.32/27 to any port 53
# ufw allow proto tcp from 192.168.0.32/27 to any port 80
# ufw allow proto tcp from 192.168.0.32/27 to any port 443
# ufw allow proto tcp from 192.168.0.64/27 to any port 22
# ufw allow proto tcp from 192.168.0.64/27 to any port 53
# ufw allow proto tcp from 192.168.0.64/27 to any port 80
# ufw allow proto tcp from 192.168.0.64/27 to any port 443
# ufw allow proto tcp from 192.168.0.64/27 to any port 22
# ufw allow proto tcp from 192.168.0.96/27 to any port 53
# ufw allow proto tcp from 192.168.0.96/27 to any port 80
# ufw allow proto tcp from 192.168.0.96/27 to any port 443
# ufw allow proto tcp from 192.168.0.96/27 to any port 22
#
# ufw allow proto udp from 192.168.0.32/27 to any port 53
# ufw allow proto udp from 192.168.0.32/27 to any port 80
# ufw allow proto udp from 192.168.0.32/27 to any port 443
# ufw allow proto udp from 192.168.0.64/27 to any port 22
# ufw allow proto udp from 192.168.0.64/27 to any port 53
# ufw allow proto udp from 192.168.0.64/27 to any port 80
# ufw allow proto udp from 192.168.0.64/27 to any port 443
# ufw allow proto udp from 192.168.0.64/27 to any port 22
# ufw allow proto udp from 192.168.0.96/27 to any port 53
# ufw allow proto udp from 192.168.0.96/27 to any port 80
# ufw allow proto udp from 192.168.0.96/27 to any port 443
# ufw allow proto udp from 192.168.0.96/27 to any port 22
