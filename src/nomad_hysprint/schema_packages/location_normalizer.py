from baseclasses.helper.naming_normalizer import NamingNormalizer

location_aliases = {
    'hyevap': 'HyVapBox',
    'hysprint evap': 'HyVapBox',
    'hyvap': 'HyVapBox',
    'hyvapbox': 'HyVapBox',
    'hzb-hyvap-box': 'HyVapBox',
    'peroval': 'HyPeroVapBox',
    'protovap': 'ProtoVapBox',
    'hytinvap': 'TinVapBox',
    'tinvap': 'TinVapBox',
    'inkvap': 'InkVapBox',
    'csmb/ evap': 'CSMB Evap',
    'csmb/evap': 'CSMB Evap',
    'iris': 'IRIS Evap',
    'iris evap': 'IRIS Evap',
    'iris hzbgloveboxes pero5evaporation': 'IRIS Evap',
    'iris-pero5 evaporation': 'IRIS Evap',
    'pero5 evaporation': 'IRIS Evap',
    'pero5 evaporation gb': 'IRIS Evap',
}

location_normalizer = NamingNormalizer(location_aliases)
