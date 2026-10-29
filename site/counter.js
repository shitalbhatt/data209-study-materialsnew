// Visitor counter. Uses the free Abacus counter API (no sign-up). Two numbers:
//  - visitors: counted once per browser (remembered in localStorage)
//  - views: counted on every page load
// Shown in the header badge (.visit-badge, every page) and the footer line (#visit-count, home page).
(function () {
  var NS = "data209-study-materialsnew", API = "https://abacus.jasoncameron.dev";
  var box = document.getElementById("visit-count");
  var badges = document.querySelectorAll(".visit-badge");
  function call(path) {
    return fetch(API + path).then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(function (j) { return j.value; });
  }
  var seen = false;
  try { seen = localStorage.getItem("data209_visitor") === "1"; } catch (e) {}
  var visitors = call((seen ? "/get/" : "/hit/") + NS + "/visitors").catch(function () {
    return seen ? null : call("/hit/" + NS + "/visitors").catch(function () { return null; });
  });
  var views = call("/hit/" + NS + "/views").catch(function () { return null; });
  Promise.all([visitors, views]).then(function (v) {
    if (!seen) { try { localStorage.setItem("data209_visitor", "1"); } catch (e) {} }
    var ok = v[0] !== null || v[1] !== null;
    var full = (v[0] !== null ? v[0].toLocaleString() + " visitors" : "") +
      (v[0] !== null && v[1] !== null ? " · " : "") +
      (v[1] !== null ? v[1].toLocaleString() + " page views" : "");
    if (box && ok) box.textContent = full;
    if (box && !ok && box.parentNode) box.parentNode.hidden = true;
    Array.prototype.forEach.call(badges, function (b) {
      if (!ok) { b.hidden = true; return; }
      b.textContent = "👁 " + (v[0] !== null ? v[0].toLocaleString() + " visitors" : v[1].toLocaleString() + " views");
      b.title = full;
    });
  });
})();
