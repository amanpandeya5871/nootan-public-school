(function () {

  (function fillAcademicYear() {
    var year = new Date().getFullYear();
    var en = year + "\u2013" + String(year + 1).slice(-2);
    var digits = "०१२३४५६७८९";
    var label =
      document.documentElement.lang === "hi"
        ? en.replace(/\d/g, function (digit) {
            return digits[Number(digit)];
          })
        : en;
    document.querySelectorAll("[data-session-year]").forEach(function (el) {
      el.textContent = label;
    });
  })();

  const NAV_BREAK = "(max-width: 960px)";
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");

  function isCompactNav() {
    return window.matchMedia(NAV_BREAK).matches;
  }

  function closeSubs() {
    if (!nav) return;
    nav.querySelectorAll(".has-sub.is-open").forEach(function (item) {
      item.classList.remove("is-open");
      var btn = item.querySelector(".sub-toggle");
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  }

  function setMenu(open) {
    if (!toggle || !nav) return;
    nav.classList.toggle("is-open", open);
    toggle.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute(
      "aria-label",
      open
        ? document.documentElement.lang === "hi"
          ? "मेनू बंद करें"
          : "Close menu"
        : document.documentElement.lang === "hi"
          ? "मेनू खोलें"
          : "Open menu"
    );
    document.body.classList.toggle("nav-open", open);
    if (!open) closeSubs();
    setHeaderHeight();
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setMenu(!nav.classList.contains("is-open"));
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (isCompactNav()) setMenu(false);
      });
    });
    nav.querySelectorAll(".has-sub").forEach(function (item) {
      var btn = item.querySelector(".sub-toggle");
      var sub = item.querySelector(".sub");
      var hideTimer;

      function canHoverNav() {
        return (
          !isCompactNav() &&
          window.matchMedia("(hover: hover) and (pointer: fine)").matches
        );
      }

      function showSub() {
        window.clearTimeout(hideTimer);
        nav.querySelectorAll(".has-sub.is-open").forEach(function (other) {
          if (other === item) return;
          other.classList.remove("is-open");
          var otherBtn = other.querySelector(".sub-toggle");
          if (otherBtn) otherBtn.setAttribute("aria-expanded", "false");
        });
        item.classList.add("is-open");
        if (btn) btn.setAttribute("aria-expanded", "true");
      }

      function hideSubSoon() {
        hideTimer = window.setTimeout(function () {
          item.classList.remove("is-open");
          if (btn) btn.setAttribute("aria-expanded", "false");
        }, 160);
      }

      if (btn) {
        btn.addEventListener("pointerenter", function (event) {
          if (event.pointerType === "mouse" && canHoverNav()) showSub();
        });
        btn.addEventListener("pointerleave", function (event) {
          if (event.pointerType === "mouse" && canHoverNav()) hideSubSoon();
        });
        btn.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          window.clearTimeout(hideTimer);
          if (canHoverNav()) {
            showSub();
            return;
          }
          if (item.classList.contains("is-open")) {
            item.classList.remove("is-open");
            btn.setAttribute("aria-expanded", "false");
          } else {
            showSub();
          }
        });
      }
      if (sub) {
        sub.addEventListener("pointerenter", function (event) {
          if (event.pointerType === "mouse" && canHoverNav()) {
            window.clearTimeout(hideTimer);
            showSub();
          }
        });
        sub.addEventListener("pointerleave", function (event) {
          if (event.pointerType === "mouse" && canHoverNav()) hideSubSoon();
        });
      }
    });
    document.addEventListener("click", function (event) {
      var t = event.target;
      if (t && t.closest && t.closest(".sub-toggle, .site-nav .sub")) return;
      closeSubs();
    });
  }

  function lastLetterRight(el) {
    var node = el.firstChild;
    while (node && node.nodeType !== 3) node = node.nextSibling;
    if (!node || !node.nodeValue) return el.getBoundingClientRect().right;
    var range = document.createRange();
    range.setStart(node, Math.max(0, node.nodeValue.length - 1));
    range.setEnd(node, node.nodeValue.length);
    return range.getBoundingClientRect().right;
  }

  function alignNavWithSchoolName() {
    var name = document.querySelector(".brand-name");
    var bar = document.querySelector(".site-nav-bar");
    var list = bar && bar.querySelector(":scope > ul");
    if (!name || !list) return;
    if (isCompactNav()) {
      list.style.width = "";
      return;
    }
    var extra = bar.querySelectorAll(".sub-toggle").length * 20;
    var width = Math.round(lastLetterRight(name) - list.getBoundingClientRect().left + extra);
    if (width > 80) list.style.width = width + "px";
  }
  function setHeaderHeight() {
    var identity = document.querySelector(".identity");
    var bar = document.querySelector(".site-nav-bar");
    if (!identity) return;
    var barH = 44;
    if (bar && !(nav && nav.classList.contains("is-open"))) {
      barH = Math.round(bar.getBoundingClientRect().height) || 44;
    }
    document.documentElement.style.setProperty(
      "--header-h",
      Math.round(identity.getBoundingClientRect().height + barH) + "px"
    );
  }

  function scheduleNavAlign() {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        alignNavWithSchoolName();
        setHeaderHeight();
      });
    });
  }
  scheduleNavAlign();
  window.addEventListener("resize", function () {
    if (!isCompactNav()) {
      setMenu(false);
      closeSubs();
    }
    scheduleNavAlign();
  });
  window.addEventListener("load", scheduleNavAlign);
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(scheduleNavAlign);
  }

  var GFORMS = {
    inquiry: {
      formId: "1FAIpQLSdPtIimkh16NXytPHBw3uJ0aWN4KsPYxQg_xprPQzuzQuH3aA",
      fields: {
        language: "532899777",
        student: "1573092801",
        father: "1515915041",
        mother: "1892754491",
        phone: "1815204909",
        email: "924933891",
        grade: "1150125187",
        inquiry: "603730931",
        query: "406282275",
      },
    },
    hiring: {
      formId: "1FAIpQLSeUXc-AzPauasCMLob119CrkMJfpQbPSkTx9KkaNV-sW8bwtA",
      fields: {
        name: "1427881240",
        address: "1761947904",
        age: "377564811",
        gender: "1911407103",
        qualification: "963297648",
        workplace: "1127572244",
        salary: "939638821",
        subjects: "511383120",
        classes: "1043269120",
        sample: "472847390",
      },
      repeat: ["subjects", "classes"],
      extra: {
        subject_other: "511383120",
      },
    },
  };

  function fieldValue(form, name) {
    var field = form.elements[name];
    if (!field) return "";
    if (field.type === "radio") {
      var checked = form.querySelector('[name="' + name + '"]:checked');
      return checked ? String(checked.value || "").trim() : "";
    }
    if (field.type === "checkbox") {
      return field.checked ? String(field.value || "").trim() : "";
    }
    return String(field.value || "").trim();
  }

  function checkedValues(form, name) {
    return Array.from(form.querySelectorAll('[name="' + name + '"]:checked')).map(function (input) {
      return String(input.value || "").trim();
    });
  }

  function showFormThanks(form) {
    var block = form.closest(".form-block");
    if (!block) return;
    form.reset();
    var button = form.querySelector('[type="submit"]');
    if (button) button.disabled = false;
    form.hidden = true;
    var thanks = block.querySelector(".form-thanks");
    if (thanks) thanks.hidden = false;
  }

  function submitGForm(form, config) {
    var body = new URLSearchParams();
    var repeat = config.repeat || [];
    var extra = config.extra || {};

    Object.keys(config.fields).forEach(function (name) {
      if (repeat.indexOf(name) >= 0) return;
      var entryId = config.fields[name];
      var value = fieldValue(form, name);
      if (name === "query") {
        var extras = [];
        var age = fieldValue(form, "age");
        var address = fieldValue(form, "address");
        if (age) extras.push("Date of birth / Age: " + age);
        if (address) extras.push("Address: " + address);
        if (value) extras.push(value);
        value = extras.join("\n");
      }
      if (name === "mother" && !value) {
        value = fieldValue(form, "father");
      }
      if (value) body.append("entry." + entryId, value);
    });

    repeat.forEach(function (name) {
      var entryId = config.fields[name];
      checkedValues(form, name).forEach(function (value) {
        if (value) body.append("entry." + entryId, value);
      });
    });

    Object.keys(extra).forEach(function (name) {
      var value = fieldValue(form, name);
      if (value) body.append("entry." + extra[name], value);
    });

    var url =
      "https://docs.google.com/forms/d/e/" + config.formId + "/formResponse";
    return fetch(url, { method: "POST", mode: "no-cors", body: body }).finally(function () {
      showFormThanks(form);
    });
  }

  document.querySelectorAll(".faq").forEach(function (root) {
    root.querySelectorAll("details").forEach(function (item) {
      item.addEventListener("toggle", function () {
        if (!item.open) return;
        root.querySelectorAll("details").forEach(function (other) {
          if (other !== item) other.removeAttribute("open");
        });
      });
    });
  });

  document.querySelectorAll("[data-gform]").forEach(function (form) {
    var key = form.getAttribute("data-gform") || "inquiry";
    var config = GFORMS[key];
    if (!config) return;
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!form.reportValidity()) return;
      var button = form.querySelector('[type="submit"]');
      if (button) button.disabled = true;
      submitGForm(form, config);
    });
  });

  function parseISODate(iso) {
    var parts = String(iso || "").split("-");
    if (parts.length !== 3) return null;
    var year = Number(parts[0]);
    var month = Number(parts[1]);
    var day = Number(parts[2]);
    if (!year || !month || !day) return null;
    return new Date(year, month - 1, day);
  }

  function startOfToday() {
    var now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  }

  function addMonths(d, months) {
    var copy = new Date(d.getFullYear(), d.getMonth() + months, 1);
    var last = new Date(copy.getFullYear(), copy.getMonth() + 1, 0).getDate();
    copy.setDate(Math.min(d.getDate(), last));
    return copy;
  }

  function noticeStage(iso) {
    var event = parseISODate(iso);
    if (!event) return "gone";
    var today = startOfToday();
    var start = new Date(event.getFullYear(), event.getMonth(), event.getDate() - 2);
    var currentEnd = new Date(event.getFullYear(), event.getMonth(), event.getDate() + 7);
    var archiveEnd = addMonths(event, 6);
    if (today < start) return "soon";
    if (today <= currentEnd) return "current";
    if (today <= archiveEnd) return "archive";
    return "gone";
  }

  function noticeTense(iso) {
    var event = parseISODate(iso);
    if (!event) return "before";
    var today = startOfToday();
    if (today < event) return "before";
    if (today.getTime() === event.getTime()) return "on";
    return "after";
  }

  function applyNoticeTense(root, iso) {
    if (!root || !iso) return;
    var tense = noticeTense(iso);
    root.querySelectorAll("[data-tense]").forEach(function (el) {
      el.hidden = el.getAttribute("data-tense") !== tense;
    });
  }

  document.querySelectorAll("[data-event-date]").forEach(function (el) {
    applyNoticeTense(el, el.getAttribute("data-event-date"));
  });

  document.querySelectorAll("[data-notice-live]").forEach(function (root) {
    var want = root.getAttribute("data-notice-live") || "current";
    var cards = Array.from(root.querySelectorAll("a.notice[data-event-date]"));
    var rows = Array.from(root.querySelectorAll("tr[data-notice][data-event-date]"));
    var shown = 0;
    cards.forEach(function (card) {
      var ok = noticeStage(card.getAttribute("data-event-date")) === want;
      card.hidden = !ok;
      if (ok) shown += 1;
    });
    rows.forEach(function (row) {
      var ok = noticeStage(row.getAttribute("data-event-date")) === want;
      row.hidden = !ok;
      if (ok) shown += 1;
    });
    var empty = root.querySelector(".notice-live-empty");
    if (empty) empty.hidden = shown > 0;
    var table = root.querySelector(".hours-table-wrap");
    if (table && rows.length) table.hidden = shown === 0;
  });

  document.querySelectorAll("[data-notice-board]").forEach(function (board) {
    var form = board.querySelector("[data-notice-filters]");
    if (!form) return;
    var classSel = form.querySelector('[name="notice-class"]');
    var catSel = form.querySelector('[name="notice-category"]');
    var search = form.querySelector('[name="notice-search"]');
    var rows = Array.from(board.querySelectorAll("tbody tr[data-notice]"));
    var empty = board.querySelector(".notice-filter-empty");
    var table = board.querySelector(".hours-table-wrap");

    function applyNoticeFilter() {
      var cls = classSel ? classSel.value : "all";
      var cat = catSel ? catSel.value : "all";
      var q = search ? String(search.value || "").trim().toLowerCase() : "";
      var live = board.getAttribute("data-notice-live") || "";
      var shown = 0;
      rows.forEach(function (row) {
        var ok = true;
        var classes = String(row.getAttribute("data-classes") || "all").split(/[\s,]+/);
        if (cls && cls !== "all" && classes.indexOf("all") < 0 && classes.indexOf(cls) < 0) ok = false;
        if (cat && cat !== "all" && row.getAttribute("data-category") !== cat) ok = false;
        if (q && String(row.getAttribute("data-search") || "").indexOf(q) < 0) ok = false;
        if (live && noticeStage(row.getAttribute("data-event-date")) !== live) ok = false;
        row.hidden = !ok;
        if (ok) shown += 1;
      });
      if (empty) empty.hidden = shown > 0;
      if (table) table.hidden = shown === 0;
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
    });
    ["change", "input"].forEach(function (evt) {
      form.addEventListener(evt, applyNoticeFilter);
    });
    applyNoticeFilter();
  });

  function startCarousel(root, itemSelector, delayMs) {
    if (!root) return;
    const items = Array.from(root.querySelectorAll(itemSelector));
    if (!items.length) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let index = items.findIndex(function (item) {
      return item.classList.contains("is-active");
    });
    if (index < 0) index = 0;
    items.forEach(function (item, idx) {
      item.classList.toggle("is-active", idx === index);
    });
    if (reduce || items.length < 2) return;
    window.setInterval(function () {
      index = (index + 1) % items.length;
      items.forEach(function (item, idx) {
        item.classList.toggle("is-active", idx === index);
      });
    }, delayMs || 4000);
  }

  startCarousel(document.querySelector("[data-quote-carousel]"), ".hero-quote", 4000);
  startCarousel(document.querySelector("[data-topper-carousel]"), ".topper-card", 6000);
  document.querySelectorAll("[data-gallery-carousel]").forEach(function (root) {
    startCarousel(root, ".gallery-slide", 4000);
  });

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function wrapPaper(el) {
    if (el.querySelector(":scope > .reveal-paper-inner")) return;
    const inner = document.createElement(el.tagName === "P" || el.tagName === "A" ? "span" : "div");
    inner.className = "reveal-paper-inner";
    while (el.firstChild) inner.appendChild(el.firstChild);
    el.appendChild(inner);
  }

  document.querySelectorAll("main .story h2, main .page h2, main .section-title, main .enquire h2").forEach(function (el) {
    el.classList.add("reveal-gold");
  });
  document.querySelectorAll("main .story p, main .story a.learn-more, main .enquire p, main .section-caption, main .sample-note").forEach(function (el) {
    el.classList.add("reveal-paper");
    wrapPaper(el);
  });
  document.querySelectorAll("main .cards, main .notice-grid, main .class-list, main .gallery-grid, main .gallery-album").forEach(function (el) {
    el.classList.add("reveal-cascade");
  });

  const nodes = document.querySelectorAll(".reveal-gold, .reveal-paper, .reveal-cascade");

  function enableReveal() {
    document.documentElement.classList.add("js");
  }

  if (!nodes.length) {
    enableReveal();
    return;
  }

  if (reduce) {
    nodes.forEach(function (el) {
      el.classList.add("is-visible");
    });
    enableReveal();
    return;
  }

  enableReveal();

  const io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        entry.target.classList.toggle("is-visible", entry.isIntersecting);
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
  );

  window.requestAnimationFrame(function () {
    window.requestAnimationFrame(function () {
      nodes.forEach(function (el) {
        io.observe(el);
      });
    });
  });
})();
