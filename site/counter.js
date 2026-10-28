// Visitor counter. Uses the free Abacus counter API (no sign-up). Two numbers:
//  - visitors: counted once per browser (remembered in localStorage)
//  - views: counted on every page load
(function () {
  var NS = "data209-study-materialsnew", API = "https://abacus.jasoncameron.dev";
  var box = document.getElementById("visit-count");
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
    if (box && (v[0] !== null || v[1] !== null)) {
      box.textContent = (v[0] !== null ? v[0].toLocaleString() + " visitors" : "") +
        (v[0] !== null && v[1] !== null ? " · " : "") +
        (v[1] !== null ? v[1].toLocaleString() + " page views" : "");
    }
  });
})();
