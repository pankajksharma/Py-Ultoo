import urllib, urllib2, cookielib, httplib,json
import os, re
from BeautifulSoup import BeautifulSoup

class pypinterestError(Exception):
    def __init__(self, description):
        self.description = description

    def __str__(self):
        return self.description

class Client:
    def __init__(self, number, password, useragent=r'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'):
            self.number = number
            self.password = password
            self.csrf = -1
            self.cj = None
            self.useragent = useragent
            self.islogin = False
            self.sessid = None 		#Session Id
            self.base = r'http://ultoo.com'

    """Basic Authentication"""
    def auth(self):
        if self.islogin == False:
            url = self.base + r'/login.php'
	   # print url
	    try:
		    os.remove(self.number+'.cookie')
		    print 'Getting Headers'
	    except:
		    print 'Getting Headers'
            cj = cookielib.LWPCookieJar()
            if os.path.isfile(self.number+'.cookie'):
                cj.revert(self.number+'.cookie', False, False)

                #check if it is expired
                for x in cj:
                    if x.name == 'csrftoken':
                        self.csrf = x.value
                        self.cj = cj

                #print 'Login successful via cookie'
                self.islogin = True
                return

            else:
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                try:
                    login_form = BeautifulSoup(opener.open(url).read())
                except (urllib2.URLError, urllib2.HTTPError, httplib.HTTPException), e:
                    raise pypinterestError('Error in login(): ' + str(e))


                opener.addheaders = [
                                ("User-agent", self.useragent),
                                ('Content-Type', 'application/x-www-form-urlencoded'),
                                ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                                ("Accept-Encoding", "gzip, deflate"),
                                ('Referer', 'http://ultoo.com/')]
                
                login_data = urllib.urlencode({'Rpidci' : '', 'LoginMobile' : self.number, 'LoginPassword' : self.password, 'RememberMe' : '1','submit2' : 'LOGIN HERE'})

                try:
                    req = urllib2.Request(url, login_data)
                    raw_html = opener.open(req).read()
		    #print raw_html
                except (urllib2.URLError, urllib2.HTTPError, httplib.HTTPException), e:
                    raise pypinterestError('Error in login(): ' + str(e))

                #test if the login was successful
                for c in cj:
		    #print c
                    #if len(c.value)=='yes':  #success login returns a longer string, but it is hard to tell exactly TODO
                    print 'Login successful'
                    self.sessid = re.findall("zxcoiesesscd=[0-9]*", raw_html)[0].split('=')[1]
                    #print self.sessid
                    self.islogin = True
                    cj.save(self.number+'.cookie', False, False)
                    self.cj = cj
                    return

                print 'Login failed'
                #raise pypinterestError('Error in login(): ' + str(e))
                return
        else:
            return

    def sendsms(self,number,message):
        self.auth()
	url = self.base + r'/home.php?zxcoiesesscd='+self.sessid
	#print url
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        opener.addheaders = [
                        ("User-agent", self.useragent),
                        ('Content-Type', 'application/x-www-form-urlencoded'),
                        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                        ('Referer', 'http://ultoo.com/')]
	mssg_data = urllib.urlencode({'MessageLength' : str(140-len(message)), 'MobileNos' : number, 'Message' : message, 'SendNow' : 'Send Now','SendNowBtn' : 'Send Now'})
        try:
            req = urllib2.Request(url,mssg_data)
            data = opener.open(req).read()
	    #print data
	    if 'ent.php' in data:
		print 'Message Sent.'
	    else:
		print 'Message Sending Failed.'
        except (urllib2.URLError, urllib2.HTTPError, httplib.HTTPException), e:
            raise pypinterestError('Error in getboards():'+ str(e))
            return None
