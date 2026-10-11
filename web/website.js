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
