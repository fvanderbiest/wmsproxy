This is a proxy made to redirect incoming getMap requests to available WMS servers based on BBOX.
It is available under the terms of the Simplified BSD License.

The config object is defined in the first lines of wmsproxy.cgi
It should have two members: a rules array and a default_service_url string.

Rules are tested in the order they are defined in the array. The first match (regarding strict inclusion) is used for proxying. If none matches, the default service url is used.

Note: bbox is defined in EPSG:4326 but any incoming projection is supported.

Example config object: 
config = {
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