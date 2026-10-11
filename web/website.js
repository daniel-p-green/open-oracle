// Presentation only. The working kiosk retains its own request/voice/erase controllers.
document.querySelectorAll('[data-open-details]').forEach(link => {
  link.addEventListener('click', event => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target instanceof HTMLDetailsElement) {
      event.preventDefault();
      target.open = true;
      target.scrollIntoView({ block: 'start' });
      target.querySelector('summary')?.focus({ preventScroll: true });
    }
  });
});

// One request owner for this landing surface; future language/voice adapters must
// consume it rather than start another controller. The kiosk has its own owner.
const ballotForm = document.getElementById('ballot-form');
if (ballotForm && window.OpenOracleIntake) {
  window.OpenOracleWebsiteOwner = window.OpenOracleIntake.createOwner();
  window.OpenOracleIntake.mount(ballotForm, window.OpenOracleWebsiteOwner);
}

// Presentation-only: nested station help remains reachable from the existing header link.
document.addEventListener('click', event => {
 const link=event.target.closest?.('a[data-open-details]');
 if(!link)return;
 const target=document.getElementById(link.getAttribute('href')?.slice(1));
 const parent=target?.closest('.station-help');
 if(parent)parent.open=true;
},true);
// Existing app-owned help/privacy actions may open a nested disclosure directly.
document.addEventListener('toggle', event => {
 const target=event.target;
 if(!(target instanceof HTMLDetailsElement)||!target.open)return;
 const parent=target.closest('.station-help');
 if(parent&&parent!==target)parent.open=true;
},true);
