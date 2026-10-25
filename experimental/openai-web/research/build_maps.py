"""Build a local-only deterministic map artifact from pinned official originals."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pyproj
import shapefile
import shapely
from shapely.geometry import shape, box
from shapely.ops import transform, unary_union

REPOSITORY = Path(__file__).resolve().parents[3]
MANIFEST = REPOSITORY / 'docs/rebuild/MAP-SOURCE-MANIFEST.json'
TARGET_CRS = 'EPSG:5070'


def pinned(inputs, name, sources):
    row = next(r for r in sources if r['name'] == name)
    data = (Path(inputs) / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != row['sha256']: raise ValueError('source_hash_mismatch')
    return data


def project(features, crs):
    conversion = pyproj.Transformer.from_crs(crs, TARGET_CRS, always_xy=True, allow_ballpark=False)
    result = {}
    for district, geometry in features:
        if district in result or district not in range(1, 9): raise ValueError('district_identity')
        if geometry.geom_type not in {'Polygon', 'MultiPolygon'} or not geometry.is_valid or geometry.is_empty:
            raise ValueError('invalid_original_geometry')
        mapped = transform(conversion.transform, geometry)
        if not mapped.is_valid or mapped.is_empty: raise ValueError('invalid_projected_geometry')
        result[district] = mapped
    if set(result) != set(range(1, 9)): raise ValueError('district_coverage')
    return result, {'description': conversion.description, 'accuracy_metres': conversion.accuracy}


def svg_path(geometry):
    polygons = [geometry] if geometry.geom_type == 'Polygon' else geometry.geoms
    parts = []
    for polygon in polygons:
        for ring in [polygon.exterior, *polygon.interiors]:
            coordinates = list(ring.coords)
            parts.append('M' + ' L'.join(f'{x:.1f},{-y:.1f}' for x, y in coordinates) + ' Z')
    return ' '.join(parts)


def view_bounds(geometry):
    x0, y0, x1, y1 = geometry.bounds
    padding = max(x1 - x0, y1 - y0) * .035
    return [x0-padding, -y1-padding, x1-x0+2*padding, y1-y0+2*padding]


def build(inputs, output):
    output = Path(output).resolve()
    if output.is_relative_to(REPOSITORY): raise ValueError('keep_derived_maps_outside_repository')
    manifest = json.loads(MANIFEST.read_text())
    sources = manifest['sources']
    for name in ['baseline-cd118.zip','hb1.geojson','baseline.pdf','hb1.pdf']: pinned(inputs,name,sources)
    raw = pinned(inputs, 'baseline-cd118.zip', sources)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        stem = 'tl_2023_29_cd118'
        reader = shapefile.Reader(shp=io.BytesIO(archive.read(stem+'.shp')), dbf=io.BytesIO(archive.read(stem+'.dbf')), shx=io.BytesIO(archive.read(stem+'.shx')))
        crs = pyproj.CRS.from_wkt(archive.read(stem+'.prj').decode())
        baseline = [(int(row.record.as_dict()['CD118FP']), shape(row.shape.__geo_interface__)) for row in reader.iterShapeRecords()]
    proposal_json = json.loads(pinned(inputs, 'hb1.geojson', sources))
    if proposal_json.get('crs', {}).get('properties', {}).get('name') != 'EPSG:4326': raise ValueError('unexpected_proposal_crs')
    proposal = [(int(f['properties']['District']), shape(f['geometry'])) for f in proposal_json['features']]
    current, current_conversion = project(baseline, crs)
    proposed, proposed_conversion = project(proposal, 'EPSG:4326')
    combined = unary_union([*current.values(), *proposed.values()])
    region_transform = pyproj.Transformer.from_crs('EPSG:4326', TARGET_CRS, always_xy=True, allow_ballpark=False)
    regions = {'statewide': combined,
               'kc': transform(region_transform.transform, box(-95.1, 38.5, -94.2, 39.6)),
               'stl': transform(region_transform.transform, box(-91.1, 38.15, -89.8, 39.2))}
    names = {'statewide':'Statewide', 'kc':'Kansas City area — fixed view', 'stl':'St. Louis area — fixed view'}
    plans = []
    for key, label, geometries, source_name, conversion in [
            ('baseline', '2022 plan — used for November 2026', current, 'baseline-cd118.zip', current_conversion),
            ('proposed', '2025 HB1 plan — referendum comparison', proposed, 'hb1.geojson', proposed_conversion)]:
        union = unary_union(list(geometries.values()))
        overlap = sum(g.area for g in geometries.values()) - union.area
        coverage_valid = bool(shapely.coverage_is_valid(list(geometries.values())))
        if not coverage_valid: raise ValueError('invalid_coverage_edges')
        if overlap > 1: raise ValueError('overlapping_district_interiors')
        plans.append({'id':key,'label':label,'source_name':source_name,'conversion':conversion,
                      'features':[{'id':district,'path':svg_path(g)} for district,g in sorted(geometries.items())],
                      'validation':{'valid_districts':8,'coverage_edges_valid':coverage_valid,'overlap_square_metres':max(0,overlap)}})
    views = []
    for key, region in regions.items():
        labels = {}
        for plan_id, geometries in [('baseline',current),('proposed',proposed)]:
            labels[plan_id] = []
            for district, g in sorted(geometries.items()):
                visible = g.intersection(region)
                if visible.is_empty or visible.area < 1: continue
                point = visible.representative_point()
                labels[plan_id].append({'id':district,'x':round(point.x,1),'y':round(-point.y,1)})
        views.append({'id':key,'label':names[key],'bounds':view_bounds(region),'labels':labels})
    output.mkdir(parents=True,exist_ok=True)
    payload = {'version':1,'purpose':'local deterministic review; no personal district inference',
               'projection':TARGET_CRS,'simplification':'none; display coordinates rounded to 0.1 metre',
               'plans':plans,'views':views,'sources':sources,
               'legal_status':'September 25 Supreme Court stay preserves the 2022 plan for November 2026; not final disposition of every challenge. Recheck before release.',
               'rights':'Publicly distributed official inputs; no blanket reuse license established. Local review only.',
               'limits':'No change-area, population, partisan-impact or shoreline-difference analysis. IDs select matching district numbers, not equivalent territory.'}
    data = json.dumps(payload,separators=(',',':')).encode()
    if len(data)>8*1024*1024: raise ValueError('derived_byte_bound')
    (output/'maps.json').write_bytes(data)
    receipt={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'projection':TARGET_CRS,'source_hashes_verified':4,
             'original_and_projected_geometry_valid':True,'districts_per_plan':[8,8],
             'geometry_dependencies':{'shapely':shapely.__version__,'pyproj':pyproj.__version__,'pyshp':shapefile.__version__},
             'limits':payload['limits'],'plans':[{'id':p['id'],'conversion':p['conversion'],'validation':p['validation']} for p in plans]}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    return payload


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();build(args.inputs,args.output)
