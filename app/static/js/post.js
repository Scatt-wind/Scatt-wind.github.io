document.addEventListener("DOMContentLoaded", function () {
    var backBtn = document.getElementById("post-back");
    if (backBtn) {
        backBtn.addEventListener("click", function () {
            if (window.history.length > 1) {
                window.history.back();
            } else {
                window.location.href = "/articles";
            }
        });
    }

    document.querySelectorAll(".article-body pre").forEach(function (pre) {
        if (pre.querySelector(".code-copy-btn")) return;

        var btn = document.createElement("button");
        btn.className = "code-copy-btn";
        btn.type = "button";
        btn.setAttribute("aria-label", "复制代码");
        btn.textContent = "复制";

        btn.addEventListener("click", function () {
            var code = pre.querySelector("code");
            var text = code ? code.textContent : pre.textContent;

            navigator.clipboard.writeText(text).then(function () {
                btn.textContent = "已复制";
                btn.classList.add("copied");
                setTimeout(function () {
                    btn.textContent = "复制";
                    btn.classList.remove("copied");
                }, 2000);
            });
        });

        pre.appendChild(btn);
    });
});
