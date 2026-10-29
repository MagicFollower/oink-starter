const test = require('node:test');
const assert = require('node:assert/strict');
const { scale, wall, clamp } = require('../../assets/js/expo-geometry.js');

test('viewer keeps small images at original size and fits oversized originals without cropping', () => {
  assert.equal(scale(160,100,800,600),1);
  assert.equal(scale(1600,1000,800,600),.5);
  assert.equal(scale(400,8000,800,600),.075);
  assert.equal(scale(8000,400,800,600),.1);
});
test('expansion uses the stricter edge for small, portrait and panoramic originals', () => {
  assert.equal(scale(160,100,800,600,'expand'),5);
  assert.equal(scale(400,8000,800,600,'expand'),.075);
  assert.equal(scale(8000,400,800,600,'expand'),.1);
  assert.equal(scale(0,0,0,0,'expand'),1);
  for (const [width,height] of [[160,100],[400,8000],[8000,400],[800,800]]) {
    for (const [vw,vh] of [[800,600],[360,620],[2400,500]]) {
      const zoom=scale(width,height,vw,vh,'expand');
      assert.ok(width*zoom <= vw && height*zoom <= vh);
      assert.ok(Math.abs(width*zoom-vw)<.001 || Math.abs(height*zoom-vh)<.001);
    }
  }
});
test('wall handles mixed aspect ratios and small widths without overlapping rows', () => {
  const ratios=[.01,1,1.5,12,.8,1,2.2,1.8,1,1];
  for(const width of [280,390,800,1440]) for(const gap of [0,6]) {
    const boxes=wall(ratios,width,width<500?156:240,gap);
    assert.equal(boxes.length,ratios.length);
    for(let i=0;i<boxes.length;i++) {
      const box=boxes[i];
      assert.ok(box.width>0&&box.height>0&&box.x>=0&&box.y>=0);
      assert.ok(box.x+box.width<=width+.001);
      if(i) {
        const before=boxes[i-1];
        assert.ok(box.y>=before.y+before.height+gap-.001 || (box.y===before.y&&box.x>=before.x+before.width+gap-.001));
      }
    }
  }
  assert.deepEqual(wall([1],0,200,6),[]);
  assert.equal(clamp(10,.1,8),8);
});
