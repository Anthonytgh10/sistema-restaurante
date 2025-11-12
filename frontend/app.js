
// Frontend para "sistema-restaurante-main" (documento solo como referencia).
// Config: por defecto usa /api del mismo host; puedes fijar otra URL base.
const API_BASE = localStorage.getItem('api_base') || `${window.location.origin}/api`;
const $ = (q,root=document)=>root.querySelector(q);

function setAPIBase(v){ localStorage.setItem('api_base', v); }
function getAccess(){ return localStorage.getItem('access'); }
function setTokens({access, refresh}){
  if(access) localStorage.setItem('access', access);
  if(refresh) localStorage.setItem('refresh', refresh);
  clearTimeout(window.__inactTimer);
  window.__inactTimer = setTimeout(()=>{ showToast('Sesión expirada.'); logout(); }, 15*60*1000);
}
function clearTokens(){ localStorage.removeItem('access'); localStorage.removeItem('refresh'); }
function authHeaders(){ const a=getAccess(); return a?{'Authorization':'Bearer '+a}:{ }; }

async function jfetch(path, opts={}){
  const res = await fetch(API_BASE + path, {
    ...opts,
    headers:{ 'Content-Type':'application/json', ...(opts.headers||{}), ...authHeaders() }
  });
  const ct = res.headers.get('content-type')||'';
  if(ct.includes('application/json')){
    const json = await res.json();
    if(!res.ok) throw json;
    return json;
  }else{
    if(!res.ok) throw new Error('Error de red');
    return res;
  }
}

function showToast(msg){ const t=$('.toast'); if(!t) return; t.textContent=msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'), 2400); }
async function doLogin(ev){
  ev?.preventDefault();
  const username = $('#login-username').value.trim();
  const password = $('#login-password').value;
  if(!username || !password) return showToast('Completa usuario y contraseña.');
  try{
    const data = await jfetch('/auth/login/', {method:'POST', body: JSON.stringify({username, password})});
    setTokens(data); localStorage.setItem('rol', data.rol||'');
    document.querySelector('.modal').classList.remove('active');
    showToast('Bienvenido 👋'); setTimeout(()=>location.href='pedidos.html', 500);
  }catch(e){ showToast((e && e.error) || 'Credenciales inválidas'); }
}
async function logout(){ try{ await jfetch('/auth/logout/', {method:'POST'}); }catch(_){}
  clearTokens(); localStorage.removeItem('rol'); location.href='index.html'; }
function requireAuth(){ if(!getAccess()) location.href='index.html'; }

// Usuarios
async function cargarUsuarios(){
  requireAuth();
  const rol = $('#f-rol').value;
  const estado = $('#f-estado').value;
  const q = $('#f-q').value.trim();
  const params = new URLSearchParams(); if(rol) params.set('rol',rol); if(estado) params.set('estado',estado); if(q) params.set('q',q);
  const data = await jfetch('/usuarios/?'+params.toString());
  const tbody = $('#usuarios-body'); tbody.innerHTML='';
  data.forEach(u=>{
    const tr = document.createElement('tr'); tr.className='tr';
    tr.innerHTML = `<td>${u.id}</td><td>${u.username}</td><td>${u.email||''}</td>
    <td><span class="badge ${u.is_active?'ok':'danger'}">${u.is_active?'Activo':'Inactivo'}</span></td>
    <td>${u.rol||'-'}</td><td>${new Date(u.date_joined).toLocaleString()}</td>
    <td style="text-align:right"><button class="btn ghost" data-action="toggle" data-id="${u.id}">${u.is_active?'Desactivar':'Reactivar'}</button></td>`;
    tbody.appendChild(tr);
  });
}
async function crearUsuario(ev){
  ev.preventDefault();
  const f = ev.target;
  const payload = { username:f.username.value.trim(), email:f.email.value.trim(), first_name:f.first_name.value.trim(), last_name:f.last_name.value.trim(), rol:f.rol.value.trim(), password:f.password.value };
  if(!payload.username || !payload.email || !payload.password) return showToast('Campos obligatorios.');
  try{ await jfetch('/usuarios/', {method:'POST', body: JSON.stringify(payload)}); showToast('Usuario creado ✅'); f.reset(); cargarUsuarios(); }
  catch(e){ showToast((e && (e.error||e.detail)) || 'Error al crear'); }
}
document.addEventListener('click', async (ev)=>{
  const btn = ev.target.closest('button'); if(!btn) return;
  if(btn.dataset.action==='toggle'){
    const id = btn.dataset.id;
    if(btn.textContent.includes('Desactivar')){
      await jfetch('/usuarios/', {method:'DELETE', body: JSON.stringify({id})}); showToast('Usuario desactivado');
    }else{
      await jfetch('/usuarios/', {method:'PATCH', body: JSON.stringify({id, is_active:true})}); showToast('Usuario reactivado');
    }
    cargarUsuarios();
  }
});

// Pedidos
async function cargarPedidos(){
  requireAuth();
  const data = await jfetch('/pedidos/');
  const tbody = $('#pedidos-body'); tbody.innerHTML='';
  data.forEach(p=>{
    const tr = document.createElement('tr'); tr.className='tr';
    tr.innerHTML = `<td>${p.id||''}</td><td>${p.numero_pedido||''}</td><td>${(p.cliente && p.cliente.nombre)||'-'}</td>
    <td><span class="badge">${p.estado}</span></td><td>${p.subtotal ?? '-'}</td><td>${p.impuesto_monto ?? '-'}</td>
    <td>${p.descuento_monto ?? '-'}</td><td><strong>${p.total ?? '-'}</strong></td><td>${new Date(p.fecha_creacion).toLocaleString()}</td>
    <td style="text-align:right">
      <button class="btn ghost" data-act="confirm" data-id="${p.id}">Confirmar</button>
      <button class="btn secondary" data-act="pay" data-id="${p.id}">Pagar</button>
      <button class="btn" style="background:#ef4444;color:#fff" data-act="cancel" data-id="${p.id}">Cancelar</button>
    </td>`; tbody.appendChild(tr);
  });
}
document.addEventListener('click', async (ev)=>{
  const b = ev.target.closest('button'); if(!b) return;
  const id = b.dataset.id; const act = b.dataset.act; if(!id || !act) return;
  try{
    if(act==='confirm'){ await jfetch(`/pedidos/${id}/confirmar/`, {method:'POST'}); showToast('Pedido confirmado'); }
    else if(act==='pay'){ const monto = prompt('Monto a registrar (vacío = total):',''); await jfetch(`/pedidos/${id}/pagar/`, {method:'POST', body: JSON.stringify({monto, metodo:'efectivo'})}); showToast('Pago registrado'); }
    else if(act==='cancel'){ const motivo = prompt('Motivo de cancelación:','N/D'); await jfetch(`/pedidos/${id}/cancelar/`, {method:'POST', body: JSON.stringify({motivo})}); showToast('Pedido cancelado'); }
    cargarPedidos();
  }catch(e){ showToast((e && (e.error||e.detail)) || 'Error'); }
});
async function descargarReporteCSV(){
  requireAuth();
  const desde = $('#r-desde').value;
  const hasta = $('#r-hasta').value;
  const cliente = $('#r-cliente').value.trim();
  const mesero = $('#r-mesero').value.trim();
  const params = new URLSearchParams(); if(desde) params.set('desde',desde); if(hasta) params.set('hasta',hasta); if(cliente) params.set('cliente',cliente); if(mesero) params.set('mesero',mesero); params.set('export','csv');
  const res = await fetch(`${API_BASE}/pedidos/reportes/?${params.toString()}`, { headers: {...authHeaders()} });
  if(!res.ok){ showToast('No se pudo descargar'); return; }
  const blob = await res.blob(); const url = URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='reportes_pedidos.csv'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}

// Reset
async function solicitarReset(ev){
  ev.preventDefault(); const email = $('#r-email').value.trim(); if(!email) return showToast('Ingresa tu correo');
  await jfetch('/auth/password/reset/', {method:'POST', body: JSON.stringify({email})}); showToast('Si el correo existe, se enviará un token.');
}
async function confirmarReset(ev){
  ev.preventDefault(); const token = $('#c-token').value.trim(); const new_password = $('#c-password').value;
  if(!token || !new_password) return showToast('Completa token y contraseña');
  await jfetch('/auth/password/confirm/', {method:'POST', body: JSON.stringify({token, new_password})}); showToast('Contraseña actualizada.');
}
