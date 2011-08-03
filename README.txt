========================================================================
                              Noodle-NG
========================================================================
          Noodle. Copyright 2009-2010 The Noodle Developers.

                               README
========================================================================

    Noodle is a web search engine for local smb/cifs network shares 
    (Windows/Samba).

    It consists of 
    - a crawler which scans a given range of IP adresses for shares, 
      collects data about shares, folders and files and stores that into
      a database 
    and 
    - a front-end for making search queries to the database.

    It is written in the powerful scripting language Python and using 
    TurboGears 2.0 as a framework for rapid web development.

 Currently in work:
========================================================================
    - proxyDownloader to download/stream files from a smb-share via http
    - extended crawler for metadata (in media files)

 Features:
========================================================================
    - Search is customizable via keywords, you can search for specific 
      file types or extensions, date of creation, etc
    - Search results are listed per host, with each host having an 
      online/offline-indicator

 Legal Notice:
========================================================================
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    An offline readable version of the GNU General Public License is 
    included in the file COPYING.txt .