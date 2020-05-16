
wget http://ftp.gnome.org/pub/gnome/sources/gnome-terminal/3.36/gnome-terminal-3.36.2.tar.xz
./configure --prefix=/usr             \
            --disable-static          \
            --disable-search-provider \
            --without-nautilus-extension &&
make
make install &&
rm -v /usr/lib/systemd/user/gnome-terminal-server.service
