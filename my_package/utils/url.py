import urllib.request
import urllib.error

# check received url whethere it exists or not.
def checkURL(url) -> bool:
    try:
        f = urllib.request.urlopen(url)
        f.close()
        return True
    except:
        return False
