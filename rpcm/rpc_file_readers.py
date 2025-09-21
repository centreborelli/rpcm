# Copyright (C) 2015-19, Carlo de Franchis <carlo.de-franchis@cmla.ens-cachan.fr>
# Copyright (C) 2015-19, Gabriele Facciolo <facciolo@cmla.ens-cachan.fr>
# Copyright (C) 2015-19, Enric Meinhardt <enric.meinhardt@cmla.ens-cachan.fr>


from xml.etree import ElementTree
import json


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
    with open(rpc_file) as f:
        rpc_content = f.read()

    if rpc_file.lower().endswith('xml'):
        try:
            rpc = read_rpc_xml(rpc_content)
        except NotImplementedError:
            raise NotImplementedError('XML file {} not supported'.format(rpc_file))
    elif rpc_file.lower().endswith('json'):
        with open(rpc_file, 'r') as f:
            rpc = json.load(f)
            assert 'rpc' in rpc, "JSON file {} does not contain 'rpc' key".format(rpc_file)
            rpc = rpc['rpc']
            d = {}
            d["LINE_OFF"] = rpc['row_offset']
            d["SAMP_OFF"] = rpc['col_offset']
            d["LAT_OFF"] = rpc['lat_offset']
            d["LONG_OFF"] = rpc['lon_offset']
            d["HEIGHT_OFF"] = rpc['alt_offset']

            d["LINE_SCALE"] = rpc['row_scale']
            d["SAMP_SCALE"] = rpc['col_scale']
            d["LAT_SCALE"] = rpc['lat_scale']
            d["LONG_SCALE"] = rpc['lon_scale']
            d["HEIGHT_SCALE"] = rpc['alt_scale']

            d["LINE_NUM_COEFF"] = " ".join([str(x) for x in rpc['row_num']])
            d["LINE_DEN_COEFF"] = " ".join([str(x) for x in rpc['row_den']])
            d["SAMP_NUM_COEFF"] = " ".join([str(x) for x in rpc['col_num']])
            d["SAMP_DEN_COEFF"] = " ".join([str(x) for x in rpc['col_den']])
            rpc = {k: d[k] for k in sorted(d)}
    else:
        # we assume that non xml rpc files follow the ikonos convention
        rpc = read_rpc_ikonos(rpc_content)

    return rpc


def read_rpc_ikonos(rpc_content):
    """
    Read RPC file assuming the ikonos format

    Args:
        rpc_content: content of RPC sidecar file path read as a string

    Returns:
        dictionary read from the RPC file

    """
    import re

    lines = rpc_content.split('\n')

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

    # if the LON/LAT coefficients are present then it must be an "extended ikonos"
    if 'LON_NUM_COEFF_1' in d:
        d['LON_NUM_COEFF']  = parse_coeff(d, "LON_NUM_COEFF", range(1, 21))
        d['LON_DEN_COEFF']  = parse_coeff(d, "LON_DEN_COEFF", range(1, 21))
        d['LAT_NUM_COEFF']   = parse_coeff(d, "LAT_NUM_COEFF" , range(1, 21))
        d['LAT_DEN_COEFF']   = parse_coeff(d, "LAT_DEN_COEFF" , range(1, 21))

    return d


def read_rpc_xml(rpc_content):
    """
    Read RPC file assuming the XML format and determine whether it's a pleiades, spot-6 or worldview image

    Args:
        rpc_content: content of RPC sidecar file path read as a string (XML format)

    Returns:
        dictionary read from the RPC file

    Raises:
        NotImplementedError: if the file format is not handled (the expected keys are not found)

    """
    # parse the xml file content
    tree = ElementTree.fromstring(rpc_content)

    # determine wether it's a pleiades, spot-6 or worldview image
    a = tree.find('Metadata_Identification/METADATA_PROFILE') # PHR_SENSOR
    b = tree.find('IMD/IMAGE/SATID') # WorldView
    c = tree.find('specific/mission')
    parsed_rpc = None
    if a is not None:
        if a.text in ['PHR_SENSOR', 'S6_SENSOR', 'S7_SENSOR']:
            parsed_rpc = read_rpc_xml_pleiades(tree)
        elif a.text in ['PNEO_SENSOR']:
            parsed_rpc = read_rpc_xml_pleiades_neo(tree)
    elif b is not None:
        if b.text == 'WV02' or b.text == 'WV01' or b.text == 'WV03':
            parsed_rpc = read_rpc_xml_worldview(tree)
    elif c is not None:
        if c.text == 'EnMAP':
            parsed_rpc = read_rpc_xml_enmap(tree)

    if not parsed_rpc:
        raise NotImplementedError()

    return parsed_rpc


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


def read_rpc_xml_pleiades_neo(tree):
    """
    Read RPC fields from a parsed XML tree assuming the pleiades NEO XML format
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
    d = tree.find('Rational_Function_Model/Global_RFM/ImagetoGround_Values')
    m['LON_NUM_COEFF'] = parse_coeff(d, "LON_NUM_COEFF", range(1, 21))
    m['LON_DEN_COEFF'] = parse_coeff(d, "LON_DEN_COEFF", range(1, 21))
    m['LAT_NUM_COEFF'] = parse_coeff(d, "LAT_NUM_COEFF", range(1, 21))
    m['LAT_DEN_COEFF'] = parse_coeff(d, "LAT_DEN_COEFF", range(1, 21))
    #m['ERR_BIAS']       = parse_coeff(d, "ERR_BIAS", ['X', 'Y'])


    ## inverse model (PROJECTION)
    i = tree.find('Rational_Function_Model/Global_RFM/GroundtoImage_Values')
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
    m['LINE_OFF'    ] = float(v.find('LINE_OFF').text)
    m['SAMP_OFF'    ] = float(v.find('SAMP_OFF').text)
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


def read_rpc_xml_enmap(tree):
    """
    Read RPC fields from a parsed XML tree assuming the EnMAP XML format.

    This reader works for L1B, L1C and L2A products.

    Args:
        tree: parsed XML tree

    Returns:
        dict: dictionary of models (dictionnaries) read from the RPC file, or
            empty dict in case of failure. There is one model per band, the
            bands numbers correspond to dictionary keys.

    """
    def parse_coeff(element, prefix, indices):
        """ helper function"""
        return ' '.join([element.find(prefix + "_" + "{:02d}".format(x)).text for x in indices])

    m = {}

    # direct model (LOCALIZATION), there is 1 model per band
    rpc_models = tree.find('product/navigation/RPC').findall("bandID")

    for band, rpc_model in enumerate(rpc_models):
        model = {}

        model['LINE_OFF'    ] = float(rpc_model.find('ROW_OFF').text)
        model['SAMP_OFF'    ] = float(rpc_model.find('COL_OFF').text)
        model['LAT_OFF'     ] = float(rpc_model.find('LAT_OFF').text)
        model['LONG_OFF'    ] = float(rpc_model.find('LONG_OFF').text)
        model['HEIGHT_OFF'  ] = float(rpc_model.find('HEIGHT_OFF').text)

        model['LINE_SCALE'  ] = float(rpc_model.find('ROW_SCALE').text)
        model['SAMP_SCALE'  ] = float(rpc_model.find('COL_SCALE').text)
        model['LAT_SCALE'   ] = float(rpc_model.find('LAT_SCALE').text)
        model['LONG_SCALE'  ] = float(rpc_model.find('LONG_SCALE').text)
        model['HEIGHT_SCALE'] = float(rpc_model.find('HEIGHT_SCALE').text)

        model['LINE_NUM_COEFF'] = parse_coeff(rpc_model, "ROW_NUM", range(1, 21))
        model['LINE_DEN_COEFF'] = parse_coeff(rpc_model, "ROW_DEN", range(1, 21))
        model['SAMP_NUM_COEFF'] = parse_coeff(rpc_model, "COL_NUM", range(1, 21))
        model['SAMP_DEN_COEFF'] = parse_coeff(rpc_model, "COL_DEN", range(1, 21))

        m[str(band+1)] = model

    return m
