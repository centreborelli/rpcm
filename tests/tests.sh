IMG="http://menthe.ovh.hw.ipol.im/IARPA_data/cloud_optimized_geotif/01SEP15WV031000015SEP01135603-P1BS-500497284040_01_P001_________AAE_0AAAAABPABP0.TIF"
rpcm footprint ${IMG}
rpcm projection ${IMG} --lon -58.6096 --lat -34.4732
rpcm localization ${IMG} -x 21377.790 -y 21481.055 -z 100
rpcm crop ${IMG} aoi.geojson c.tif
rpcm projection ${IMG} --lon -58.602 --lat -34.488 --crop c.tif
