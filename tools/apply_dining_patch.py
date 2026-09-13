from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'id="diningLocation"' in s:
    print('Dining log already present')
    raise SystemExit(0)

s=s.replace('.noteBox{width:100%;min-height:68px;padding:10px;border-radius:12px;border:1px solid color-mix(in srgb,CanvasText 18%,transparent);background:Canvas;margin-top:8px}', '.noteBox{width:100%;min-height:68px;padding:10px;border-radius:12px;border:1px solid color-mix(in srgb,CanvasText 18%,transparent);background:Canvas;margin-top:8px}.diningGrid{display:grid;grid-template-columns:1fr;gap:8px}.diningGrid input,.diningGrid textarea{width:100%;padding:12px;border-radius:12px;border:1px solid color-mix(in srgb,CanvasText 18%,transparent);background:Canvas}.diningGrid textarea{min-height:58px}.diningGrid button{border-radius:12px;padding:12px;border:1px solid color-mix(in srgb,CanvasText 18%,transparent);background:CanvasText;color:Canvas;font-weight:700}.entry-kind{font-size:.68rem;text-transform:uppercase;letter-spacing:.06em;opacity:.55;margin-bottom:2px}')

needle='<section>\n  <div class="section-title">Today’s log</div>'
insert='<section>\n  <div class="section-title">Dining log</div>\n  <div class="diningGrid">\n    <input id="diningLocation" list="recentDiningLocations" placeholder="Restaurant / food location" />\n    <datalist id="recentDiningLocations"></datalist>\n    <input id="diningItems" placeholder="What did you get? (optional)" />\n    <textarea id="diningNote" placeholder="Optional dining note"></textarea>\n    <button onclick="addDiningEntry()">Add dining entry</button>\n  </div>\n</section>\n\n<section>\n  <div class="section-title">Today’s log</div>'
assert needle in s
s=s.replace(needle,insert,1)

old="function addCustom(){const el=document.getElementById('customAttraction');const name=el.value.trim();if(!name)return;addCheckin(name,'Custom',currentPark);el.value=''}"
new=old+"\nfunction addDiningEntry(){const loc=document.getElementById('diningLocation').value.trim();if(!loc)return toast('Enter a dining location');const items=document.getElementById('diningItems').value.trim();const note=document.getElementById('diningNote').value.trim();const log=loadLog();log.push({id:crypto.randomUUID?crypto.randomUUID():String(Date.now())+Math.random(),type:'dining',dining_location:loc,items,timestamp:new Date().toISOString(),note});saveLog(log);document.getElementById('diningLocation').value='';document.getElementById('diningItems').value='';document.getElementById('diningNote').value='';renderAll();toast('Dining logged: '+loc)}"
assert old in s
s=s.replace(old,new,1)

s=s.replace("function undoLast(){const log=loadLog();if(!log.length)return toast('Nothing to undo');const x=log.pop();saveLog(log);renderAll();toast('Removed: '+x.attraction)}", "function undoLast(){const log=loadLog();if(!log.length)return toast('Nothing to undo');const x=log.pop();saveLog(log);renderAll();toast('Removed: '+(x.type==='dining'?x.dining_location:x.attraction))}",1)
s=s.replace("function countsByName(){const m={};for(const x of loadLog())m[x.park+'|'+x.attraction]=(m[x.park+'|'+x.attraction]||0)+1;return m}", "function countsByName(){const m={};for(const x of loadLog()){if(x.type==='dining')continue;m[x.park+'|'+x.attraction]=(m[x.park+'|'+x.attraction]||0)+1}return m}",1)

start=s.index('function renderLog()')
end=s.index('function renderStats()',start)
s=s[:start]+"function renderLog(){const log=loadLog();const root=document.getElementById('log');root.innerHTML='';if(!log.length){root.innerHTML='<div class=\"muted\">No entries yet.</div>';return}for(const x of [...log].reverse()){const e=document.createElement('div');e.className='entry';e.innerHTML=`<div class=\"entry-top\"><div><div class=\"entry-kind\"></div><span class=\"entry-name\"></span><div class=\"ride-meta\"></div></div><div class=\"entry-time\"></div></div><div class=\"entry-note hidden\"></div>`;const dining=x.type==='dining';e.querySelector('.entry-kind').textContent=dining?'Dining':'Attraction';e.querySelector('.entry-name').textContent=dining?x.dining_location:x.attraction;e.querySelector('.ride-meta').textContent=dining?(x.items||'Meal / snack'):(x.park==='DL'?'Disneyland':'DCA')+(x.land?' • '+x.land:'');e.querySelector('.entry-time').textContent=fmtTime(x.timestamp);if(x.note){const n=e.querySelector('.entry-note');n.textContent=x.note;n.classList.remove('hidden')}root.appendChild(e)}}\n"+s[end:]

s=s.replace("function renderStats(){const log=loadLog();document.getElementById('totalCount').textContent=log.length;document.getElementById('uniqueCount').textContent=new Set(log.map(x=>x.park+'|'+x.attraction)).size;document.getElementById('lastTime').textContent=log.length?fmtTime(log[log.length-1].timestamp):'—'}", "function renderStats(){const log=loadLog();const rides=log.filter(x=>x.type!=='dining');document.getElementById('totalCount').textContent=rides.length;document.getElementById('uniqueCount').textContent=new Set(rides.map(x=>x.park+'|'+x.attraction)).size;document.getElementById('lastTime').textContent=log.length?fmtTime(log[log.length-1].timestamp):'—'}\nfunction renderDiningRecent(){const dl=document.getElementById('recentDiningLocations');if(!dl)return;const seen=new Set();dl.innerHTML='';for(const x of [...loadLog()].reverse()){if(x.type!=='dining'||!x.dining_location||seen.has(x.dining_location))continue;seen.add(x.dining_location);const o=document.createElement('option');o.value=x.dining_location;dl.appendChild(o);if(seen.size>=8)break}}",1)
s=s.replace('function renderAll(){renderRides();renderLog();renderStats()}', 'function renderAll(){renderRides();renderLog();renderStats();renderDiningRecent()}',1)

start=s.index('function exportCSV()')
end=s.index('function backupPayload()',start)
s=s[:start]+"function exportCSV(){const log=loadLog();const rows=[['date','time','timestamp','entry_type','park','attraction','land','dining_location','items','note'],...log.map(x=>[fmtDate(x.timestamp),fmtTime(x.timestamp),x.timestamp,x.type==='dining'?'dining':'attraction',x.park||'',x.attraction||'',x.land||'',x.dining_location||'',x.items||'',x.note||''])];download('disney_day_log_'+new Date().toISOString().slice(0,10)+'.csv',rows.map(r=>r.map(csvEscape).join(',')).join('\\n'),'text/csv')}\n"+s[end:]
s=s.replace("function backupPayload(){return {format:'Disneyland Quick Check-In Backup',version:2,exported_at:new Date().toISOString(),checkins:loadLog()}}", "function backupPayload(){return {format:'Disneyland Day Log Backup',version:3,exported_at:new Date().toISOString(),checkins:loadLog()}}",1)

p.write_text(s,encoding='utf-8')
print('Dining log added')
