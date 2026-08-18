(function () {
  document.documentElement.classList.add("js");

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
    nav.querySelectorAll(".sub-toggle").forEach(function (btn) {
      btn.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        var item = btn.closest(".has-sub");
        var open = !item.classList.contains("is-open");
        closeSubs();
        item.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
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

  function startCarousel(root, itemSelector) {
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
    }, 4000);
  }

  startCarousel(document.querySelector("[data-quote-carousel]"), ".hero-quote");
  startCarousel(document.querySelector("[data-topper-carousel]"), ".topper-card");

  const extra = document.querySelectorAll(
    "main .story h2, main .story p, main .story a.learn-more, main .page h2, main .page p, main .page li, main .page details, main .page form, main .page dl, main .gallery-slot, main .enquire h2, main .enquire p, main .section-title, main .section-label"
  );
  extra.forEach(function (el) {
    el.classList.add("reveal");
  });

  const nodes = document.querySelectorAll(".reveal");
  if (!nodes.length) return;

  function inView(el) {
    const rect = el.getBoundingClientRect();
    return rect.bottom > 0 && rect.top < (window.innerHeight || 0);
  }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    nodes.forEach(function (el) {
      el.classList.add("is-visible");
    });
    return;
  }

  const io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.01, rootMargin: "0px 0px -8px 0px" }
  );
  nodes.forEach(function (el) {
    if (inView(el)) {
      el.classList.add("is-visible");
      return;
    }
    io.observe(el);
  });
})();
