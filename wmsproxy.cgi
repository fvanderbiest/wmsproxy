#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""This is a proxy that we use to redirect to available WMS servers based on BBOX"""

config = {
    # rules are tested in the order they are defined.
    # the first match (regarding strict inclusion) is used for proxying    
    # if none matches, the default service url is used
    # Note: bbox is defined in epsg:4326 but any incoming projection is supported
    'rules': [{
        'bbox': [-5, 41, 10, 51], # France
        'service_url': 'http://www.ifremer.fr/services/wms1?',
        'layers': 'france_metropolitaine'
    },{
        'bbox': [-10, 35, 15, 55], # Europe
        'service_url': 'http://www.ifremer.fr/services/wms1?',
        'layers': 'Europe'
    }],
    'default_service_url': 'http://www.ifremer.fr/services/wms1?'
}

# DO NOT MODIFY ANYTHING BELOW THIS #
# (unless you know what you're doing)

import cgi
import sys, os

try:
    from osgeo import ogr
except:
    import ogr

try:
    from osgeo import osr
except:
    import osr


''' Gets a CGI var '''
def getVar(key, d):
    if d.has_key(key.lower()):
        return d[key.lower()][0]
    elif d.has_key(key.upper()):
        return d[key.upper()][0]
    else:
        return None


''' Checks whether coord2 is between coord1 and coord3 '''
def isBetween(coord1, coord2, coord3):
    return ((coord1 <= coord2) and (coord2 <= coord3))


'''Checks that bbox a is strictly included in bbox b'''
def checkBboxInclusion(a, b):
    return (isBetween(b[0], a[0], b[2]) and isBetween(b[1], a[1], b[3]) and isBetween(b[0], a[2], b[2]) and isBetween(b[1], a[3], b[3]))


'''Converts a bbox to string'''
def bbox2String(bbox):
    return (','.join([str(o) for o in bbox]))

def redirect(url):
    print "Status: 302 Found"
    print "Location: "+url
    print

query_string = os.environ['QUERY_STRING']
d = cgi.parse_qs(query_string)

debug = d.has_key("DEBUG") or d.has_key("debug")
if debug:
    print "Status: 200 OK"
    print "Content-Type: text/plain"
    print
    print "QUERY_STRING = "+query_string

request = getVar('request', d)
width = getVar('width', d)
height = getVar('height', d)
bbox = getVar('bbox', d)
srs = getVar('srs', d)

if ((request == None) or (request.upper() != 'GETMAP') or (width == None) or (width == 0) or (height == None) or (height == 0) or (bbox == None) or (srs == None)):
    if debug:
        print "Redirecting to default service url ..."
    redirect(config['default_service_url'] + query_string)
    sys.exit(0)

bbox = bbox.split(',')
bbox = [float(o) for o in bbox]

# reproject bbox to EPSG:4326 if required:
if (srs.upper() != 'EPSG:4326'):
    epsg4326 = osr.SpatialReference()
    epsg4326.ImportFromEPSG(4326)

    inputSRS = osr.SpatialReference()
    inputSRS.ImportFromEPSG(int(srs.split(':')[1]))

    toWGS = osr.CoordinateTransformation(inputSRS,epsg4326)

    lb = ogr.Geometry(ogr.wkbPoint)

    lb.AddPoint(bbox[0],bbox[1])
    rt = ogr.Geometry(ogr.wkbPoint)

    rt.AddPoint(bbox[2],bbox[3])

    lt = ogr.Geometry(ogr.wkbPoint)
    lt.AddPoint(bbox[0],bbox[3])
    rb = ogr.Geometry(ogr.wkbPoint)
    rb.AddPoint(bbox[2],bbox[1])

    lb.Transform(toWGS)
    rt.Transform(toWGS)
    lt.Transform(toWGS)
    rb.Transform(toWGS)

    left = min(lb.GetX(),lt.GetX())
    bottom = min(lb.GetY(),rb.GetY())
    right = max(rb.GetX(),rt.GetX())
    top = max(lt.GetY(),rt.GetY())
    bbox = [left, bottom, right, top]
    if debug:
        print "REPROJECTED BBOX = "+bbox2String(bbox)+'\n'

url = config['default_service_url'] + query_string

for rule in config['rules']:
    if debug:
        print "Checking rule: "+rule['layers']
        print "Is bbox "+bbox2String(bbox)+" included in "+bbox2String(rule['bbox'])+" ?" 

    if (checkBboxInclusion(bbox, rule['bbox'])):
        if debug:
            print "Yes"
        
        parts = query_string.split('&')
        qstr = {}
        for part in parts:
            kv = part.split('=')
            if (len(kv)==2):
                qstr[kv[0]] = kv[1]
        
        qstr['LAYERS'] = rule['layers']
        
        parts = {}
        for key,val in qstr.iteritems():
            parts[key+'='+val] = '-'
        
        url = rule['service_url'] + '&'.join(parts)

        break
    elif debug:
        print 'No => checking next rule ...\n'

redirect(url)
