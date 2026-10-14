#!/usr/bin/env python3
"""Independently check Rental data against a locally retained artifact bundle."""

from pathlib import Path
import csv,struct,hashlib,collections
import argparse
from ndspy.rom import NintendoDSRom
from ndspy.narc import load
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--artifacts', type=Path, required=True, help='Local artifact-bundle root containing rom/ and analysis/research-checkout/')
parser.add_argument('--output', type=Path, required=True, help='Destination for the independently recomputed JSON summary')
args = parser.parse_args()
ROOT = args.artifacts.resolve()
ret= NintendoDSRom.fromFile(ROOT/'rom/retail-source/Pokemon - Black Version 2 (USA, Europe) (NDSi Enhanced).nds')
dev= NintendoDSRom.fromFile(ROOT/'rom/development-build/main.srl')
inputs={}
for p in ('a/2/5/7','a/0/0/2','a/0/1/6','a/2/4/7'):
    b=ret.files[ret.filenames.idOf(p)]
    print('retail resource',p,'id',ret.filenames.idOf(p),'retained matches',b==(ROOT/'rom/retail-extracted'/p).read_bytes(),'sha',hashlib.sha256(b).hexdigest())
    inputs[p]=load(b)[1]
b=dev.files[dev.filenames.idOf('a/2/7/1')]
print('development rental equals retail',b==ret.files[ret.filenames.idOf('a/2/5/7')])
rental=inputs['a/2/5/7']; text=inputs['a/0/0/2']; personal=inputs['a/0/1/6']
print('count and sizes',len(rental),collections.Counter(map(len,rental)))
# Decode message entry backwards from terminator; independently verify all names with ROM.
def msg(b):
    sections,count=struct.unpack_from('<HH',b)
    sec=struct.unpack_from('<I',b,12)[0]
    out=[]
    for i in range(count):
        start,n,_=struct.unpack_from('<IHH',b,sec+4+i*8)
        words=list(struct.unpack_from('<'+'H'*n,b,sec+start)); key=words[-1]^65535
        for j in reversed(range(n)):
            words[j]^=key; key=(key>>3|key<<13)&65535
        assert words[-1]==65535
        out.append(''.join(chr(w) for w in words[:-1]))
    return out
species=msg(text[90]); moves=msg(text[403]); items=msg(text[64]); abilities=msg(text[374])
natures='Hardy Lonely Brave Adamant Naughty Bold Docile Relaxed Impish Lax Timid Hasty Serious Jolly Naive Modest Mild Quiet Bashful Rash Calm Gentle Sassy Careful Quirky'.split()
rows=list(csv.DictReader((ROOT/'analysis/research-checkout/data/rental-pokemon-builds.csv').open()))
errors=[]
assert [int(r['archive_index']) for r in rows]==list(range(1,989))
for row in rows:
    i=int(row['archive_index']); mon,*rest=struct.unpack('<H4HBBHH',rental[i]); m=rest[:4]; mask,nature,item,form=rest[4:]
    expect={'species':species[mon],'nature':natures[nature],'held_item':items[item],'form':'Default' if form==0 else str(form),'friendship':str(0 if 218 in m else 255)}
    expect.update({'move_'+str(j+1):moves[x] for j,x in enumerate(m)})
    statkeys=('ev_hp','ev_attack','ev_defense','ev_speed','ev_sp_attack','ev_sp_defense'); count=mask.bit_count()
    expect.update({k:str(min(255,510//count) if mask&(1<<j) else 0) for j,k in enumerate(statkeys)})
    p=personal[mon]; a=[abilities[p[24]]]
    if p[25] and p[25]!=p[24]: a.append(abilities[p[25]])
    expect['ability_rule']=a[0]+' (only normal ability)' if len(a)==1 else 'PID selects '+' or '.join(a)
    ratio=p[18]; ratios={31:'12.5%',63:'25%',127:'50%',191:'75%'}
    expect['gender_rule']={0:'Male',254:'Female',255:'Genderless'}.get(ratio,'PID-derived ('+ratios.get(ratio,f'{ratio/256*100:g}%')+' female)')
    names=('HP','Attack','Defense','Speed','Sp. Atk','Sp. Def')
    expect['ev_distribution']=' / '.join(expect[k]+' '+name for k,name in zip(statkeys,names) if expect[k]!='0') or 'None'
    if i<=132: tournament,tier='Rental','Weak'
    elif i<=208: tournament,tier='Rental','Strong'
    elif i<=558: tournament,tier='Rental Master','Weak'
    elif i<=908: tournament,tier='Rental Master','Strong'
    else: tournament,tier='Excluded from PWT','Not selectable'
    expect.update(tournament=tournament,tier=tier)
    expect['player_ivs']='20 in every stat' if i<=908 else 'Not applicable (excluded from PWT)'
    expect['opponent_ivs']=('Fixed by actual opponent Trainer: all 8 or all 20' if i<=208 else '20 in every stat (all eligible Trainers)') if i<=908 else 'Not applicable (excluded from PWT)'
    for k,v in expect.items():
        if row[k]!=v:errors.append((i,k,row[k],v))
print('CSV field mismatches:',len(errors))
assert not errors, errors[:10]
print('zero placeholder ids',[i for i,b in enumerate(rental) if not any(b)])
for lo,hi in [(1,132),(133,208),(209,558),(559,908),(909,988)]:
    recs=[struct.unpack('<H4HBBHH',rental[i]) for i in range(lo,hi+1)]; ids=collections.Counter(r[0] for r in recs)
    print('range',lo,hi,'count',len(recs),'species',len(ids),'multiplicities',collections.Counter(ids.values()),'form',set(r[-1] for r in recs),'duplicate records',len(recs)-len(set(recs)))
    if lo==209: weak=set(ids)
    if lo==559: print('weak vs strong species equality',weak==set(ids))
    if lo==909:print('excluded species',[species[s] for s in ids])
# Cross-check Overlay 55 directly from ROM and table bounds from actual pointer data.
for ov_id in [55]:
    o=dev.loadArm9Overlays([ov_id])[ov_id]; data=bytes(o.data); base=o.ramAddress
    print('dev overlay',ov_id,'base',hex(base),'len',len(data),'retained matches',data==(ROOT/'rom/development-build/overlays/055.bin').read_bytes())
    for addr in [0x223949c,0x22394a0]:print('range ptr literal',hex(addr),hex(struct.unpack_from('<I',data,addr-base)[0]))
    print('range table 16-bit values',struct.unpack_from('<12H',data,0x223a3ec-base))
    print('active count table',[data[0x2239b36-base+i*8] for i in range(4)])
# Fixed power metadata.
table=inputs['a/2/4/7'][0]; records=[table[i:i+16] for i in range(0,len(table),16)]
for cup,bit in [(12,3),(13,5)]:
    rs=[(i,r[8]&7,r[8]>>3) for i,r in enumerate(records) if r[5]&(1<<bit)]
    print('eligible trainer priority/power cup',cup,collections.Counter((pri,pow) for _,pri,pow in rs),'len',len(rs))
print('78-127 power metadata',set(r[8]>>3 for r in records[78:128]))
# Ace tables in runtime ROM use shared NORMAL Pokémon archive, not generated ace PD.
dtable=load(dev.files[dev.filenames.idOf('a/2/6/1')])[1][0]
aceids=[i for i in range(128) if int.from_bytes(dtable[i*16+14:i*16+16],'little')]
print('ROM ace marker count',len(aceids),'ids',aceids)
import re
markdown=(ROOT/'analysis/research-checkout/data/wbt-party-selection.md').read_text()
listed={int(m.group(1)):m.group(2) for m in re.finditer(r'^\| (\d{3}) \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|',markdown,re.M)}
for family,tp,pp in [(1,'a/2/6/2','a/2/6/4'),(2,'a/2/6/5','a/2/6/7'),(3,'a/2/6/8','a/2/7/0')]:
 tf=load(dev.files[dev.filenames.idOf(tp)])[1]; pf=load(dev.files[dev.filenames.idOf(pp)])[1]
 errs=[]; decoded={}
 for i in aceids:
  if i+1>=len(tf):continue
  ty,n,idx=struct.unpack_from('<HHH',tf[i+1]); s=struct.unpack_from('<H',pf[idx])[0]; decoded[i]=s
  if species[s]!=listed[i].strip():errs.append((i,s,species[s],listed[i]))
 print('ace family',family,'trainer count',len(tf),'pokemon count',len(pf),'ace count',len(decoded),'irrelevant family/name mismatches',len(errs))
print('Markdown ace list equals ROM ace list',set(listed)==set(aceids))
import json
summary={'rental_csv_rows_checked':len(rows),'rental_csv_field_mismatches':errors,'zero_placeholder_ids':[i for i,b in enumerate(rental) if not any(b)],'rental_pools':[],'ace_marker_ids':aceids,'runtime_ace_archives':[],'rival':{'ordinary_trainer_ids':[368,369,370],'retail_td_path':'a/0/9/1','retail_pd_path':'a/0/9/2','party_order':{}}}
for lo,hi in [(1,132),(133,208),(209,558),(559,908),(909,988)]:
 rs=[struct.unpack('<H4HBBHH',rental[i]) for i in range(lo,hi+1)]; ct=collections.Counter(r[0] for r in rs)
 summary['rental_pools'].append({'inclusive_range':[lo,hi],'records':len(rs),'species':len(ct),'per_species':sorted(set(ct.values())),'forms':sorted(set(r[-1] for r in rs))})
for family,tp,pp in [(1,'a/2/6/2','a/2/6/4'),(2,'a/2/6/5','a/2/6/7'),(3,'a/2/6/8','a/2/7/0')]:
 tf=load(dev.files[dev.filenames.idOf(tp)])[1];pf=load(dev.files[dev.filenames.idOf(pp)])[1]; eligible=[]; mismatches=[];resolved=[]
 for i in aceids:
  if i+1>=len(tf):continue
  rec=dtable[i*16:i*16+16]; idx=struct.unpack_from('<H',tf[i+1],4)[0];s=struct.unpack_from('<H',pf[idx])[0];assert s
  yes=(bool(rec[5]&(1|2|16)) if family==1 else 5<=rec[6]<=9 if family==2 else rec[6]==1 or bool(rec[5]&(4|64)) or rec[7]<=17)
  resolved.append(i)
  if yes:
   eligible.append(i)
   if listed[i].strip()!=species[s]:mismatches.append([i,listed[i],species[s]])
 summary['runtime_ace_archives'].append({'family':family,'td_path':tp,'pd_path':pp,'total_members_including_dummy':len(tf),'resolved_ace_rows':len(resolved),'eligible_ace_rows':len(eligible),'eligible_name_mismatches':mismatches})
for tid in [368,369,370]:
 td=load(ret.files[ret.filenames.idOf('a/0/9/1')])[1][tid];pd=load(ret.files[ret.filenames.idOf('a/0/9/2')])[1][tid]
 summary['rival']['party_order'][tid]=[{'species':species[struct.unpack_from('<H',pd,j*8+4)[0]&1023],'level':struct.unpack_from('<H',pd,j*8+2)[0],'iv_all':pd[j*8]*31//255}for j in range(td[3])]
args.output.write_text(json.dumps(summary,indent=2)+'\n')
print('JSON summary written', args.output)
print('eligible ace coverage',summary['runtime_ace_archives'])
