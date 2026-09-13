(function () {
  var editor = document.getElementById("editor");
  var form = document.getElementById("articleForm");
  var bodyField = document.getElementById("bodyField");
  var csrf = document.getElementById("csrf");
  if (!editor || !form) return;

  document.getElementById("toolbar").addEventListener("click", function (e) {
    var btn = e.target.closest("button");
    if (!btn) return;
    e.preventDefault();
    var cmd = btn.getAttribute("data-cmd");
    editor.focus();
    if (cmd === "h2" || cmd === "h3") {
      document.execCommand("formatBlock", false, cmd);
    } else if (cmd === "ul") {
      document.execCommand("insertUnorderedList");
    } else if (cmd === "blockquote") {
      document.execCommand("formatBlock", false, "blockquote");
    } else if (cmd === "link") {
      var url = window.prompt("Dirección del enlace (https://…)");
      if (url) document.execCommand("createLink", false, url);
    } else if (cmd === "image") {
      pickImage();
    } else {
      document.execCommand(cmd);
    }
  });

  function pickImage() {
    var input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = function () {
      var file = input.files && input.files[0];
      if (!file) return;
      var data = new FormData();
      data.append("file", file);
      data.append("csrf", csrf.value);
      fetch("/admin/subir", { method: "POST", body: data })
        .then(function (r) { return r.json(); })
        .then(function (json) {
          if (json.ok) {
            editor.focus();
            document.execCommand("insertImage", false, json.url);
          } else {
            window.alert(json.error || "No se pudo subir la foto.");
          }
        })
        .catch(function () { window.alert("No se pudo subir la foto."); });
    };
    input.click();
  }

  form.addEventListener("submit", function () {
    bodyField.value = editor.innerHTML;
  });
})();
