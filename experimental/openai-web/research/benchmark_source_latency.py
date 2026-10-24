"""Controlled local-only comparison: b10 source versus parallel source loading."""
import argparse, json, pathlib, subprocess, sys, threading, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--map-review-dir',type=pathlib.Path,required=True)
    parser.add_argument('--report',type=pathlib.Path)
    args=parser.parse_args()
    import server
    baseline = subprocess.check_output(['git','show','b10c05b:experimental/openai-web/web/experience.mjs'],text=True,cwd=ROOT.parents[1])
    baseline='import { createViewTiming } from "./view-timing.mjs";\n'+baseline
    baseline=baseline.replace('  currentTicket = ticket;\n  let mapsVerified = false;', '  currentTicket = ticket;\n  const timing = createViewTiming(workspace,"view",()=>session.current(ticket));\n  let mapsVerified = false;')
    baseline=baseline.replace('async function renderMaps(ticket) {','async function renderMaps(ticket,timing) {').replace('await renderMaps(ticket);','await renderMaps(ticket,timing);')
    baseline=baseline.replace('    c.append(originalDetails);','    c.append(originalDetails);\n    timing.mark("first_source");\n    timing.paint("first_useful_visual");')
    baseline=baseline.replace('  renderComplete = true;','  renderComplete = true;\n  timing.mark("stable_view");')
    # Same successful-map criterion; metadata instrumentation only.
    baseline=baseline.replace('      });\n    } catch {\n      if (!session.current(ticket)) return;\n      host.textContent','      });\n      timing.mark("maps_validated");\n    } catch {\n      if (!session.current(ticket)) return;\n      host.textContent',1)
    if 'timing.mark("maps_validated")' not in baseline: raise RuntimeError("baseline_instrumentation_failed")
    original=server.Handler.do_GET
    records=[];started=time.monotonic()
    def get(self):
        if self.path=='/experience.mjs' and self.server.baseline:
            self.reply(200,baseline.encode(),'text/javascript; charset=utf-8');return
        delay={'/proposition-a.json':.150,'/maps.json':.350,'/map-status.json':.550}.get(self.path,0)
        if delay:
            records.append({'port':self.server.server_port,'path':self.path,'start_ms':round((time.monotonic()-started)*1000,2),'delay_ms':delay*1000})
            if args.report: args.report.write_text(json.dumps(records,indent=2)+'\n')
            threading.Event().wait(delay)
        try:return original(self)
        except (BrokenPipeError,ConnectionResetError):pass
    server.Handler.do_GET=get
    apps=[]
    for port,old in [(8915,True),(8916,False)]:
        app=server.make_server(port,map_review_dir=args.map_review_dir)
        app.baseline=old;apps.append(app)
        threading.Thread(target=app.serve_forever,daemon=True).start()
    print('Provider-off local comparison: baseline8915, parallel8916; fixed150/350/550ms public source delays',flush=True)
    try:threading.Event().wait()
    except KeyboardInterrupt:pass
    finally:
        for app in apps:app.shutdown();app.server_close()

if __name__ == "__main__":
    main()
