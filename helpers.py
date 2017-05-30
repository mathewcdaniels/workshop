import shutil, os, zipfile, glob, html
import urllib.request

def header(outfile):
    """Writes the header information for each .xhtml file."""
    with open("header", "r") as header:
        while True:
            head = header.readline()
            if not head:
                break

            outfile.writelines(head)

    header.close()

def ePub(filename, title, author, isbn):
    """Writes the .xhtml files for the chapters."""
    file_num = 1
    file_open = False
    outfile = None
    infile = '/home/ubuntu/workspace/ePubCreator/uploads/' + filename
    
    shutil.copytree("model", "tmp")
    
    # if ISBN is provided fetch cover image
    if isbn != '':
        cover(isbn)
        
    # Create & open new title page file
    title_page = 'tmp/OEBPS/Text/title_page.xhtml'
    with open(title_page, 'w') as outfile: 
        if outfile == None:
            raise("Unable to create {}".format(outfile))
        
        header(outfile)
    
        outfile.write('<body>\n  <div>\n   <p>&nbsp;</p>\n\n    <h2 id="heading_id_2">' + title + '</h2>\n\n\
        <p>&nbsp;</p>\n\n    <h3 id="heading_id_4">' + author + '</h3>\n  </div>\n</body>\n</html>')
    
    with open(infile, "r") as infile:
        if infile == None:
            raise("Unable to open {}.".format(infile))
        
        while True:
            text = infile.readline()
            if not text:
                outfile.write("</p>\n  </div>\n</body>\n</html>")
                break
    
            elif text.startswith(('#', 'Chapter', 'CHAPTER')):
                if file_open == True:
                    outfile.write("</p>\n  </div>\n</body>\n</html>")
                    outfile.close()
                    file_open = False
                    file_num += 1
    
                # Create & open new file
                chapter = 'tmp/OEBPS/Text/chap{:02d}.xhtml'.format(file_num)
    
                outfile = open(chapter, 'w')
                if outfile == None:
                    raise("Unable to create {}".format(outfile))
    
                file_open = True
    
                # Write header information to chapter
                header(outfile)
    
                outfile.write("<body>\n  <div>\n   <h3>" + html.escape(text.lstrip('#')) + "</h3>\n<p>")
    
            # Complete writing the chapter
            elif file_open == True:
                if text.endswith('\n'):
                    outfile.writelines(html.escape(text))
                    outfile.write("</p>\n<p>")
    
                else:
                    outfile.writelines(html.escape(text))
    
    toc(file_num)
    content(file_num)
    
    outfile.close()
    
    cleanup('uploads')
    
    return package(title)

def cover(isbn):
    """Fetches the cover image from Open Library Covers API on the Internet Archive."""
    cover_url = 'http://covers.openlibrary.org/b/isbn/{}-L.jpg?default=false'.format(isbn)
    try:
        urllib.request.urlretrieve(cover_url, "tmp/OEBPS/Images/Cover.jpg")
    except urllib.request.HTTPError: pass
    
def toc(chapters):
    """Creates the 'toc.ncx' file for Table of Contents"""
    with open("toc_head", "r") as header:
        TOC = open("tmp/OEBPS/toc.ncx", "w")
        
        while True:
            head = header.readline()
            if not head:
                break
            TOC.writelines(head)

        for chapter in range(1, chapters + 1):
            entry = """\
        <navPoint id="navPoint-{0:}" playOrder="{0:}">
            <navLabel>
                <text>Chapter {1:}</text>
            </navLabel>
            <content src="Text/chap{1:02d}.xhtml"/>
        </navPoint>
""".format(chapter + 2, chapter)
            
            TOC.write(entry)

        closetags = """\
    </navMap>
</ncx>"""
        
        TOC.write(closetags)

        TOC.close()

def content(chapters):
    """Creates the 'content.opf' file."""
    with open("cont_head", "r") as header:
        content = open("tmp/OEBPS/content.opf", "w")
        
        while True:
            head = header.readline()
            if not head:
                break
            content.writelines(head)

        for chapter in range(1, chapters + 1):
            entry = ('\t\t<item id="chap{0:02d}.xhtml" href="Text/chap{0:02d}.xhtml" media-type="application/xhtml+xml"/>\n').format(chapter)
            
            content.write(entry)

        midtags = ("""\
    </manifest>
    <spine toc="ncx">
        <itemref idref="cover.xhtml"/>
        <itemref idref="title_page.xhtml"/>
""")
        
        content.write(midtags)

        for chapter in range(1, chapters + 1):
            entry = ('\t\t<itemref idref="chap{0:02d}.xhtml"/>\n').format(chapter)
            
            content.write(entry)

        endtags = ('\t</spine>\n'
                '</package>\n')

        content.write(endtags)
        content.close()

def package(title):
    """Packs up the ePub file and transfers it to the download directory"""
    cleanup('downloads')
    epub_name = title.lower().replace(' ','_') + '.epub'
    
    os.chdir(os.path.join('tmp'))
    
    with zipfile.ZipFile('/home/ubuntu/workspace/ePubCreator/downloads/' + epub_name, "w") as f:
         
        f.write("mimetype", compress_type=zipfile.ZIP_STORED)
        os.remove('mimetype')
        
        for folder in os.curdir:
            # https://www.experts-exchange.com/questions/23254293/Adding-directories-to-a-ZipFile.html
            dirname = os.path.join(folder)
            
            for dirpath, dirnames, filenames in os.walk(dirname):
                for fname in filenames:
                    fullname = os.path.join(dirpath, fname)
                    f.write(fullname, compress_type=zipfile.ZIP_DEFLATED)
    
    os.chdir('..')
    
    shutil.rmtree('tmp')
    
    return (epub_name)

def cleanup(dir_to_clean):
    """Removes uploaded files."""
    folder = glob.glob(os.path.join(dir_to_clean + '/*'))
    
    # http://stackoverflow.com/questions/1995373/deleting-all-files-in-a-directory-with-python/1995397/#1995397
    for file in folder:
        os.remove(file)