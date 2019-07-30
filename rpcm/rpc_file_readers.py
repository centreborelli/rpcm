# Copyright (C) 2015-19, Carlo de Franchis <carlo.de-franchis@cmla.ens-cachan.fr>
# Copyright (C) 2015-19, Gabriele Facciolo <facciolo@cmla.ens-cachan.fr>
# Copyright (C) 2015-19, Enric Meinhardt <enric.meinhardt@cmla.ens-cachan.fr>


from __future__ import print_function
import copy
import numpy as np
from xml.etree.ElementTree import ElementTree


def read_rpc_file(rpc_file):
    """
    Read RPC from a file deciding the format from the extension of the filename.  
      xml          : spot6, pleiades, worldview  
      txt (others) : ikonos 
    
    Args:
        rpc_file: RPC sidecar file path

    Returns:
        dictionary read from the RPC file, or an empty dict if fail 

    """

    if rpc_file.lower().endswith('xml'):
        ## check if the xml is formatted as xml
        #tree = ElementTree()
        #tree.parse(rpc_file)
        return read_rpc_xml(rpc_file)
    else:
        # we assume that non xml rpc files follow the ikonos convention
        return read_rpc_ikonos(rpc_file)


def read_rpc_ikonos(rpc_file):
    """
    Read RPC file assuming the ikonos format 
    
    Args:
        rpc_file: RPC file path

    Returns:
        dictionary read from the RPC file

    """
    import re

    lines = open(rpc_file).read().split('\n')

    d = {}
    for l in lines:
        ll = l.split()
        if len(ll) > 1: 
            k = re.sub(r"[^a-zA-Z0-9_]","",ll[0])
            d[k] = ll[1]

    def parse_coeff(dic, prefix, indices):
        """ helper function"""
        return ' '.join([dic["%s_%s" % (prefix, str(x))] for x in indices])

    d['SAMP_NUM_COEFF']  = parse_coeff(d, "SAMP_NUM_COEFF", range(1, 21))
    d['SAMP_DEN_COEFF']  = parse_coeff(d, "SAMP_DEN_COEFF", range(1, 21))
    d['LINE_NUM_COEFF']  = parse_coeff(d, "LINE_NUM_COEFF", range(1, 21))
    d['LINE_DEN_COEFF']  = parse_coeff(d, "LINE_DEN_COEFF", range(1, 21))

    return d



def read_rpc_xml(rpc_file):
    """
    Read RPC file assuming the XML format and determine wether it's a pleiades, spot-6 or worldview image
    
    Args:
        rpc_file: RPC sidecar file path (XML formart)

    Returns:
        dictionary read from the RPC file, or empty dict in case of failure

    """

    # read the xml file content
    tree = ElementTree()
    tree.parse(rpc_file)

    # determine wether it's a pleiades, spot-6 or worldview image
    a = tree.find('Metadata_Identification/METADATA_PROFILE') # PHR_SENSOR
    b = tree.find('IMD/IMAGE/SATID') # WorldView
    if a is not None:
        if a.text in ['PHR_SENSOR', 'S6_SENSOR', 'S7_SENSOR']:
            return read_rpc_xml_pleiades(tree)
        else:
            print('unknown sensor type')
    elif b is not None:
        if b.text == 'WV02' or b.text == 'WV01' or b.text == 'WV03':
            return read_rpc_xml_worldview(tree)
        else:
            print('unknown sensor type')
    return {}


def read_rpc_xml_pleiades(tree):
    """
    Read RPC fields from a parsed XML tree assuming the pleiades, spot-6 XML format
    Also reads the inverse model parameters 
    
    Args:
        tree: parsed XML tree

    Returns:
        dictionary read from the RPC file, or empty dict in case of failure

    """
    m = {}

    def parse_coeff(element, prefix, indices):
        """ helper function"""
        return ' '.join([element.find("%s_%s" % (prefix, str(x))).text for x in indices])

    # direct model (LOCALIZATION)
    d = tree.find('Rational_Function_Model/Global_RFM/Direct_Model')
    m['LON_NUM_COEFF'] = parse_coeff(d, "SAMP_NUM_COEFF", range(1, 21))
    m['LON_DEN_COEFF'] = parse_coeff(d, "SAMP_DEN_COEFF", range(1, 21))
    m['LAT_NUM_COEFF'] = parse_coeff(d, "LINE_NUM_COEFF", range(1, 21))
    m['LAT_DEN_COEFF'] = parse_coeff(d, "LINE_DEN_COEFF", range(1, 21))
    #m['ERR_BIAS']       = parse_coeff(d, "ERR_BIAS", ['X', 'Y'])

    
    ## inverse model (PROJECTION)
    i = tree.find('Rational_Function_Model/Global_RFM/Inverse_Model')
    m['SAMP_NUM_COEFF']  = parse_coeff(i, "SAMP_NUM_COEFF", range(1, 21))
    m['SAMP_DEN_COEFF']  = parse_coeff(i, "SAMP_DEN_COEFF", range(1, 21))
    m['LINE_NUM_COEFF']  = parse_coeff(i, "LINE_NUM_COEFF", range(1, 21))
    m['LINE_DEN_COEFF']  = parse_coeff(i, "LINE_DEN_COEFF", range(1, 21))
    m['ERR_BIAS']        = parse_coeff(i, "ERR_BIAS", ['ROW', 'COL'])
    
    # validity domains
    v = tree.find('Rational_Function_Model/Global_RFM/RFM_Validity')
    #vd = v.find('Direct_Model_Validity_Domain')
    #m.firstRow = float(vd.find('FIRST_ROW').text)
    #m.firstCol = float(vd.find('FIRST_COL').text)
    #m.lastRow  = float(vd.find('LAST_ROW').text)
    #m.lastCol  = float(vd.find('LAST_COL').text)

    #vi = v.find('Inverse_Model_Validity_Domain')
    #m.firstLon = float(vi.find('FIRST_LON').text)
    #m.firstLat = float(vi.find('FIRST_LAT').text)
    #m.lastLon  = float(vi.find('LAST_LON').text)
    #m.lastLat  = float(vi.find('LAST_LAT').text)

    # scale and offset
    # the -1 in line and column offsets is due to Pleiades RPC convention
    # that states that the top-left pixel of an image has coordinates
    # (1, 1)
    m['LINE_OFF'    ] = float(v.find('LINE_OFF').text) - 1
    m['SAMP_OFF'    ] = float(v.find('SAMP_OFF').text) - 1
    m['LAT_OFF'     ] = float(v.find('LAT_OFF').text)
    m['LONG_OFF'    ] = float(v.find('LONG_OFF').text)
    m['HEIGHT_OFF'  ] = float(v.find('HEIGHT_OFF').text)
    m['LINE_SCALE'  ] = float(v.find('LINE_SCALE').text)
    m['SAMP_SCALE'  ] = float(v.find('SAMP_SCALE').text)
    m['LAT_SCALE'   ] = float(v.find('LAT_SCALE').text)
    m['LONG_SCALE'  ] = float(v.find('LONG_SCALE').text)
    m['HEIGHT_SCALE'] = float(v.find('HEIGHT_SCALE').text)

    return m


def read_rpc_xml_worldview(tree):
    """
    Read RPC fields from a parsed XML tree assuming the worldview XML format
    
    Args:
        tree: parsed XML tree

    Returns:
        dictionary read from the RPC file, or empty dict in case of failure

    """
    m = {}

    # inverse model (PROJECTION)
    im = tree.find('RPB/IMAGE')
    l = im.find('LINENUMCOEFList/LINENUMCOEF')
    m['LINE_NUM_COEFF'] =  l.text 
    l = im.find('LINEDENCOEFList/LINEDENCOEF')
    m['LINE_DEN_COEFF'] =  l.text 
    l = im.find('SAMPNUMCOEFList/SAMPNUMCOEF')
    m['SAMP_NUM_COEFF'] =  l.text 
    l = im.find('SAMPDENCOEFList/SAMPDENCOEF')
    m['SAMP_DEN_COEFF'] =  l.text 
    m['ERR_BIAS'] = float(im.find('ERRBIAS').text)

    # scale and offset
    m['LINE_OFF'    ] = float(im.find('LINEOFFSET').text)
    m['SAMP_OFF'    ] = float(im.find('SAMPOFFSET').text)
    m['LAT_OFF'     ] = float(im.find('LATOFFSET').text)
    m['LONG_OFF'    ] = float(im.find('LONGOFFSET').text)
    m['HEIGHT_OFF'  ] = float(im.find('HEIGHTOFFSET').text)
    
    m['LINE_SCALE'  ] = float(im.find('LINESCALE').text)
    m['SAMP_SCALE'  ] = float(im.find('SAMPSCALE').text)
    m['LAT_SCALE'   ] = float(im.find('LATSCALE').text)
    m['LONG_SCALE'  ] = float(im.find('LONGSCALE').text)
    m['HEIGHT_SCALE'] = float(im.find('HEIGHTSCALE').text)


#    # image dimensions
#    m.lastRow = int(tree.find('IMD/NUMROWS').text)
#    m.lastCol = int(tree.find('IMD/NUMCOLUMNS').text)

    return m


