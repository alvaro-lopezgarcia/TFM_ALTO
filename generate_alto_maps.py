#!/usr/bin/env python3
"""
Simple script to validate ALTO network map and cost map generation using BGP and BGP-LS.

Before using this script, please install requirements:

    pip install -U networkx

Usage:

    ./generate_alto_maps.py <path-to-bgp-ipv4-rib-json> <path-to-bgp-ls-rib-json>
"""
import sys
import json
import base64
import networkx
sys.path.insert(1, '/home/centos/Alto')
from alto_client.alto_client import AltoClient

DEFAULT_ASN = 0


def load_jsondb(routes, path=None):
    if path is None:
        path = []
    db = json.loads(routes)
    for k in path:
        db = db[k]
    return db


def load_topo(lsdb):
    topo = networkx.DiGraph()
    for lsa in lsdb:
        if 'link-descriptors' in lsa:
            src = get_router_id(lsa['local-node-descriptors'])
            dst = get_router_id(lsa['remote-node-descriptors'])
            topo.add_edge(src, dst)
        if 'prefix-descriptors' in lsa:
            origin = get_router_id(lsa['advertising-node-descriptors'])
            prefix = lsa['prefix-descriptors']['ip-reachability-information']
            if origin not in topo.nodes():
                topo.add_node(origin)
            if 'prefixes' not in topo.node[origin]:
                topo.node[origin]['prefixes'] = []
            topo.node[origin]['prefixes'].append(prefix)
        if 'node-descriptors' in lsa:
            n = get_router_id(lsa['node-descriptors'])
            if n not in topo.nodes():
                topo.add_node(n)
    return topo


def get_router_id(router):
    if 'ospf-node' in router:
        return router['ospf-node']['ospf-router-id']
    elif 'ospf-pseudonode' in router:
        return router['ospf-pseudonode']['ospf-router-id']
    elif 'isis-node' in router:
        return decode_iso_system_id(router['isis-node']['iso-system-id'])
    elif 'isis-pseudonode' in router:
        return decode_iso_system_id(router['isis-pseudonode']['is-is-router-identifier']['iso-system-id'])


def decode_iso_system_id(iso_system_id):
    return eval('0x' + base64.b64decode(iso_system_id).hex())


def load_pidprop(lsdb):
    props = dict()
    for lsa in lsdb:
        if 'node-descriptors' in lsa:
            if 'ospf-node' in lsa['node-descriptors']:
                pidname = 'pid%d:%s' % (DEFAULT_ASN, get_origin_hex(lsa['node-descriptors']['ospf-node']['ospf-router-id']))
                desc = lsa['node-descriptors']
                origin = (desc['as-number'], desc.get('domain-id', 0), desc.get('area-id', 0), get_router_id(desc))
                if pidname not in props:
                    props[pidname] = []
                props[pidname].append(origin)
            if 'isis-node' in lsa['node-descriptors']:
                pidname = 'pid%d:%s' % (DEFAULT_ASN, get_origin_hex1(lsa['attributes']['node-attributes']['ipv4-router-id']))
                desc = lsa['node-descriptors']
                origin = (desc['as-number'], desc.get('domain-id', 0), desc.get('area-id', 0), get_router_id(desc))
                if pidname not in props:
                    props[pidname] = []
                props[pidname].append(origin)
    return props


def load_pids(ipv4db):
    pids = dict()
    for r in ipv4db:
        prefix = r['prefix']
        pidname = 'pid%d:%s' % (DEFAULT_ASN, get_origin_hex1(r['attributes']['ipv4-next-hop']['global']))
        if pidname not in pids:
            pids[pidname] = []
        pids[pidname].append(prefix)
    return pids


def compute_costmap0(topo, pids, props):
    shortest_paths = dict(networkx.shortest_paths.all_pairs_dijkstra_path_length(topo))
    costmap = dict()
    for src in pids:
        sp = props.get(src, [(0, None)])[0][-1]
        costmap[src] = dict()
        for dst in pids:
            dp = props.get(dst, [(0, None)])[0][-1]
            if sp is not None and dp is not None:
                costmap[src][dst] = shortest_paths.get(sp, {}).get(dp, 64)
    return costmap


def get_origin_hex(ip):
    return ''.join(['%08x' % int(ip)])


def get_origin_hex1(ip):
    return ''.join(['%02x' % int(w) for w in ip.split('.')])


def print_nodes(lsdb):
    print('\n'.join(['topology.addNode(%dL, %dL);' % (lsa['node-descriptors'].get('area-id', 0),
                                                      get_router_id(lsa['node-descriptors']))
                     for lsa in lsdb if 'node-descriptors' in lsa]))


def print_links(lsdb):
    print('\n'.join(['topology.addLink("%s", %dL, %dL, %dL);' % (lsa['route-key'],
                                                                 lsa['local-node-descriptors'].get('area-id', 0),
                                                                 get_router_id(lsa['local-node-descriptors']),
                                                                 get_router_id(lsa['remote-node-descriptors']))
                     for lsa in lsdb if 'link-descriptors' in lsa]))


def print_intra_prefix(lsdb):
    print('\n'.join(['topology.addIntraPrefix("%s", %dL, %dL);' %
                     (lsa['prefix-descriptors']['ip-reachability-information'],
                      lsa['advertising-node-descriptors'].get('area-id', 0),
                      get_router_id(lsa['advertising-node-descriptors']))
                     for lsa in lsdb if 'prefix-descriptors' in lsa and
                     (lsa['protocol-id'] == 'isis-level1' or
                      lsa['prefix-descriptors'].get('ospf-route-type') == 'intra-area')]))


def print_inter_prefix(lsdb):
    print('\n'.join(['topology.addInterPrefix("%s", %dL, %dL, %dL);' %
                     (lsa['prefix-descriptors']['ip-reachability-information'],
                      lsa['advertising-node-descriptors'].get('area-id', 0),
                      get_router_id(lsa['advertising-node-descriptors']),
                      lsa['attributes']['prefix-attributes']['prefix-metric'])
                     for lsa in lsdb if 'prefix-descriptors' in lsa
                     and (lsa['protocol-id'] == 'isis-level2' or
                          lsa['prefix-descriptors'].get('ospf-route-type') == 'inter-area')]))


if __name__ == '__main__':

    catalog_client = AltoClient(port='8181', user='admin', password='admin')
    bgp_routes_json = catalog_client.invoke_api(method='get', path='bgp/loc-rib/tables/bgp-types:ipv4-address-family/'
                                                                   'bgp-types:unicast-subsequent-address-family/'
                                                                   'ipv4-routes')
    ls_routes_json = catalog_client.invoke_api(method='get', path='bgp/loc-rib/tables/bgp-linkstate:'
                                                                  'linkstate-address-family/bgp-linkstate:'
                                                                  'linkstate-subsequent-address-family/linkstate-routes')

    ipv4db = load_jsondb(json.dumps(bgp_routes_json), path=['bgp-inet:ipv4-routes', 'ipv4-route'])
    lsdb = load_jsondb(json.dumps(ls_routes_json), path=['bgp-linkstate:linkstate-routes', 'linkstate-route'])
    topo = load_topo(lsdb)

    props = load_pidprop(lsdb)
    pids = load_pids(ipv4db)
    costmap = compute_costmap0(topo, pids, props)
    print(json.dumps(pids, indent=2, sort_keys=True))
    print('='*32)
    # print(json.dumps(props, indent=2, sort_keys=True))
    # print('='*32)
    print(json.dumps(costmap, indent=2, sort_keys=True))
    with open('networkmap.json', 'w') as outfile:
        json.dump(pids, outfile, indent=2)
    with open('costmap.json', 'w') as outfile:
        json.dump(costmap, outfile)