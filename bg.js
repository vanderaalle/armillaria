function initBg(label) {
  const c = document.getElementById('bg');
  const ctx = c.getContext('2d');
  const seed = Math.random() * 0xffffffff | 0;

  function draw() {
    c.width = window.innerWidth;
    c.height = window.innerHeight;
    const W = c.width, H = c.height;
    let r = seed;
    function rand() { r=(r*1664525+1013904223)&0xffffffff; return (r>>>0)/0xffffffff; }
    function rng(a,b) { return a+rand()*(b-a); }
    function dist(a,b) { const dx=a[0]-b[0],dy=a[1]-b[1]; return Math.sqrt(dx*dx+dy*dy); }
    const nodes = [];
    for (let i=0; i<55; i++) nodes.push([rng(0,W), rng(0,H)]);
    ctx.lineCap = 'round';
    for (let i=0; i<nodes.length; i++) {
      const sorted = nodes.map((n,j)=>[dist(nodes[i],n),j]).filter(([d,j])=>j!==i).sort((a,b)=>a[0]-b[0]);
      const k = rand()>0.4 ? 3 : 2;
      for (let c2=0; c2<k; c2++) {
        const j=sorted[c2][1];
        if (j<i) continue;
        const ax=nodes[i][0],ay=nodes[i][1],bx=nodes[j][0],by=nodes[j][1];
        const mx=(ax+bx)/2+rng(-18,18), my=(ay+by)/2+rng(-18,18);
        ctx.strokeStyle='rgba(255,255,255,0.09)';
        ctx.lineWidth=0.7;
        ctx.beginPath(); ctx.moveTo(ax,ay); ctx.quadraticCurveTo(mx,my,bx,by); ctx.stroke();
      }
    }
    ctx.strokeStyle='rgba(255,255,255,0.045)';
    ctx.lineWidth=0.4;
    for (const [nx,ny] of nodes) {
      const hairs=3+Math.floor(rand()*3);
      for (let h=0; h<hairs; h++) {
        const angle=rand()*Math.PI*2, len=rng(8,28);
        const ex=nx+Math.cos(angle)*len, ey=ny+Math.sin(angle)*len;
        const mx=(nx+ex)/2+rng(-5,5), my=(ny+ey)/2+rng(-5,5);
        ctx.beginPath(); ctx.moveTo(nx,ny); ctx.quadraticCurveTo(mx,my,ex,ey); ctx.stroke();
      }
    }
    ctx.fillStyle='rgba(255,255,255,0.12)';
    for (const [nx,ny] of nodes) {
      ctx.beginPath(); ctx.arc(nx,ny,0.8,0,Math.PI*2); ctx.fill();
    }
    ctx.save();
    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(255,255,255,0.04)';
    ctx.font = '700 ' + Math.floor(W*0.13) + 'px Georgia, serif';
    ctx.fillText(label, W/2, H/2 + Math.floor(W*0.05));
    ctx.font = '400 ' + Math.floor(W*0.022) + 'px monospace';
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    ctx.fillText('AV MXXVI', W/2, H/2 + Math.floor(W*0.10));
    ctx.restore();
  }
  draw();
  window.addEventListener('resize', draw);
}
