import urllib2
import os

__author__ = 'Cespinosa'


class Downloader(object):
    def __init__(self):
        pass

    def downloadFile(self, url, downloadPath, retry=0):
        try:
            if os.path.exists(downloadPath) and os.path.getsize(downloadPath) > 0:
                return
            directory = os.path.dirname(downloadPath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                          urllib2.HTTPHandler(debuglevel=0),
                                          urllib2.HTTPSHandler(debuglevel=0))
            opener.addheaders = [
                ('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'),
                ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                ('Connection', 'keep-alive')]

            resp = opener.open(url, timeout=60)
            contentLength = resp.info()['Content-Length']
            totalSize = float(contentLength)
            currentSize = 0
            dl_file = open(downloadPath, 'wb')
            CHUNK_SIZE = 32 * 1024
            while True:
                data = resp.read(CHUNK_SIZE)
                if not data:
                    break
                currentSize += len(data)
                dl_file.write(data)
            if currentSize >= totalSize:
                dl_file.close()
        except Exception, x:
            print 'Error downloading: '
            print x