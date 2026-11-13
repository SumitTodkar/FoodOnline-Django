/* FoodOnline front-end behaviour. Plain JavaScript: no dependencies besides Bootstrap's bundle. */
(function () {
  'use strict';

  // ---- Toast notifications -------------------------------------------------
  function showToast(message, level) {
    var container = document.getElementById('toast-container');
    if (!container) { return; }
    var type = ['success', 'error', 'warning', 'info'].indexOf(level) > -1 ? level : 'info';
    var el = document.createElement('div');
    el.className = 'toast align-items-center fo-toast ' + type;
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    el.innerHTML = '<div class="d-flex"><div class="toast-body"></div>' +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>';
    el.querySelector('.toast-body').textContent = message; // textContent keeps this XSS-safe
    container.appendChild(el);

    if (window.bootstrap && window.bootstrap.Toast) {
      var toast = new window.bootstrap.Toast(el, { delay: 2800 });
      el.addEventListener('hidden.bs.toast', function () { el.remove(); });
      toast.show();
    } else {
      el.classList.add('show');
      setTimeout(function () { el.remove(); }, 2800);
    }
  }

  function updateCartBadges(count) {
    document.querySelectorAll('[data-cart-count]').forEach(function (badge) {
      badge.textContent = count;
      badge.hidden = !count;
    });
  }

  // ---- Add to cart without a page reload -------------------------------------
  document.addEventListener('submit', function (event) {
    var form = event.target;
    if (!form.classList || !form.classList.contains('js-add-to-cart')) { return; }
    event.preventDefault();

    var button = form.querySelector('button[type="submit"]');
    var originalHtml = button ? button.innerHTML : '';
    if (button) {
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>';
    }

    fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin'
    })
      .then(function (response) { return response.json(); })
      .then(function (data) {
        updateCartBadges(data.count);
        showToast(data.message, data.level);
      })
      .catch(function () {
        form.submit(); // fall back to a normal form post
      })
      .finally(function () {
        if (button) {
          button.disabled = false;
          button.innerHTML = originalHtml;
        }
      });
  });

  // ---- Quantity stepper on the food detail page ---------------------------------
  document.querySelectorAll('[data-qty-step]').forEach(function (button) {
    button.addEventListener('click', function () {
      var input = button.parentElement.querySelector('input[type="number"]');
      if (!input) { return; }
      var min = parseInt(input.min || '1', 10);
      var max = parseInt(input.max || '20', 10);
      var next = (parseInt(input.value, 10) || min) + parseInt(button.dataset.qtyStep, 10);
      input.value = Math.max(min, Math.min(max, next));
    });
  });

  // ---- Auto-submit filter selects ---------------------------------------------------
  document.querySelectorAll('[data-autosubmit]').forEach(function (control) {
    control.addEventListener('change', function () {
      if (control.form) { control.form.submit(); }
    });
  });

  // ---- Navbar shadow after scrolling ------------------------------------------------
  var navbar = document.querySelector('.fo-navbar');
  if (navbar) {
    var onScroll = function () { navbar.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---- Prevent double submission of forms that create data ------------------------------
  document.querySelectorAll('form[data-once]').forEach(function (form) {
    form.addEventListener('submit', function () {
      var button = form.querySelector('button[type="submit"]');
      if (button) {
        setTimeout(function () { button.disabled = true; }, 0);
      }
    });
  });
})();
