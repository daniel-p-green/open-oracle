// Accept only this fixed, locally generated review shape. No arbitrary HTML/URLs.
export function validateMaps(data, registry) {
  if (data?.version !== 1 || data.projection !== 'EPSG:5070' || data.plans?.length !== 2 || data.views?.length !== 3) throw Error('map_shape');
  if (JSON.stringify(data.sources) !== JSON.stringify(registry.sources)) throw Error('map_sources');
  const planIds = ['baseline', 'proposed'];
  const finite = n => typeof n === 'number' && Number.isFinite(n);
  if (data.views.map(v => v.id).join() !== 'statewide,kc,stl') throw Error('map_views');
  for (const [i, plan] of data.plans.entries()) {
    if (plan.id !== planIds[i] || plan.features?.map(f => f.id).join() !== '1,2,3,4,5,6,7,8' || plan.validation?.coverage_edges_valid !== true) throw Error('map_districts');
    for (const feature of plan.features) if (typeof feature.path !== 'string' || feature.path.length > 1_000_000 || !/^[MLZ 0-9,.\-]+$/.test(feature.path)) throw Error('map_path');
    if (typeof plan.label !== 'string' || plan.label.length > 120) throw Error('map_label');
  }
  for (const view of data.views) {
    if (typeof view.label !== 'string' || view.label.length > 100 || view.bounds?.length !== 4 || !view.bounds.every(finite) || view.bounds[2] <= 0 || view.bounds[3] <= 0) throw Error('map_bounds');
    for (const id of planIds) {
      const labels = view.labels?.[id];
      if (!Array.isArray(labels) || labels.length > 8 || new Set(labels.map(l => l.id)).size !== labels.length) throw Error('map_labels');
      for (const label of labels) if (!Number.isInteger(label.id) || label.id < 1 || label.id > 8 || !finite(label.x) || !finite(label.y)) throw Error('map_labels');
    }
  }
  return structuredClone(data);
}
