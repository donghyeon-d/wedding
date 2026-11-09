import { createRequire } from 'module'; const sharp = createRequire('/home/dongchoi/wedding/web/package.json')('sharp');
// 실행: cd web && npm install && node ../tools/photos/gallery.mjs  (photo_v3/의 1-1, 1-2 … 3-7 순서로 01.jpg~ 생성)
import fs from 'fs';
const src='/home/dongchoi/wedding/web/photo_v3/', out='/home/dongchoi/wedding/web/src/assets/gallery/';
const key=f=>f.match(/^(\d+)-(\d+)/).slice(1).map(Number);
const files=fs.readdirSync(src).filter(f=>/^\d+-\d+\./.test(f)).sort((a,b)=>{const[x,y]=key(a),[p,q]=key(b);return x-p||y-q;});
for (const f of fs.readdirSync(out)) fs.unlinkSync(out+f);
for (const [i,f] of files.entries()){
  const n=String(i+1).padStart(2,'0');
  const info=await sharp(src+f).rotate().resize(2400,2400,{fit:'inside',withoutEnlargement:true}).flatten({background:'#fff'}).jpeg({quality:85,mozjpeg:true}).toFile(out+n+'.jpg');
  console.log(n, f, info.width+'x'+info.height, Math.round(info.size/1024)+'KB');
}
