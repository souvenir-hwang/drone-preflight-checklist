// 관리 화면 공통: 세션 단위 PIN 게이트
// 허브(admin.html)든 하위 화면(admin-drones.html, admin-items.html)이든
// 이 세션에서 한 번 PIN을 맞히면 다시 묻지 않는다(sessionStorage 기준, 탭/브라우저 재시작 시 초기화).
const ADMIN_PIN = 'SHIDroneCheck';
const SUPABASE_URL = 'https://qsqrobfkipbgmmgedcnu.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFzcXJvYmZraXBiZ21tZ2VkY251Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ2MzE1OTMsImV4cCI6MjEwMDIwNzU5M30.oeTPzxFDMz7k5DZdztkGy6IqwKskE7nMcEEMgyABZw0';
const SB_HEADERS = {'apikey': SUPABASE_ANON_KEY, 'Authorization': 'Bearer '+SUPABASE_ANON_KEY};

function adminGate(onPass){
  if(sessionStorage.getItem('admin_gate') === '1'){
    onPass();
    return;
  }
  const overlay = document.createElement('div');
  overlay.style.cssText = 'position:fixed;inset:0;background:#f2f4f8;z-index:100;display:flex;align-items:center;justify-content:center;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif;';
  overlay.innerHTML = `
    <div style="background:#fff;border:1px solid #e2e6ee;border-radius:12px;padding:26px;max-width:320px;width:90%;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,.08);">
      <div style="font-size:16px;font-weight:700;color:#1428A0;margin-bottom:16px;">🔒 관리 화면 PIN 입력</div>
      <input type="password" id="adminPinInput" autocomplete="off"
        style="width:100%;padding:11px;border:1px solid #e2e6ee;border-radius:8px;font-size:14px;margin-bottom:10px;box-sizing:border-box;" placeholder="PIN">
      <button id="adminPinBtn" style="width:100%;padding:11px;border:none;border-radius:8px;background:#1428A0;color:#fff;font-weight:700;font-size:14px;cursor:pointer;">확인</button>
      <div id="adminPinErr" style="color:#d23b3b;font-size:12px;margin-top:10px;min-height:14px;"></div>
    </div>`;
  document.body.appendChild(overlay);
  const input = overlay.querySelector('#adminPinInput');
  const btn = overlay.querySelector('#adminPinBtn');
  const err = overlay.querySelector('#adminPinErr');
  function tryPass(){
    if(input.value === ADMIN_PIN){
      sessionStorage.setItem('admin_gate','1');
      overlay.remove();
      onPass();
    }else{
      err.textContent = 'PIN이 일치하지 않습니다.';
      input.value='';
      input.focus();
    }
  }
  btn.addEventListener('click', tryPass);
  input.addEventListener('keydown', e=>{ if(e.key==='Enter') tryPass(); });
  input.focus();
}
