(function () {
    var grid = document.querySelector(".about-skill-grid");
    var detail = document.getElementById("about-skill-detail");
    if (!grid || !detail) {
        return;
    }

    var placeholder = detail.querySelector(".about-skill-detail-placeholder");
    var body = detail.querySelector(".about-skill-detail-body");
    var titleEl = detail.querySelector(".about-skill-detail-title");
    var descEl = detail.querySelector(".about-skill-detail-desc");
    var tiles = grid.querySelectorAll(".about-skill-tile");
    var activeSkill = null;

    function clearActive() {
        tiles.forEach(function (tile) {
            tile.classList.remove("is-active");
            tile.setAttribute("aria-expanded", "false");
        });
    }

    function showPlaceholder() {
        activeSkill = null;
        clearActive();
        if (placeholder) {
            placeholder.hidden = false;
        }
        if (body) {
            body.hidden = true;
        }
        detail.classList.remove("is-open");
    }

    function showSkill(skillId) {
        var template = document.getElementById("skill-detail-" + skillId);
        if (!template || !titleEl || !descEl || !body) {
            return;
        }

        var titleNode = template.content.querySelector("[data-title]");
        var descNode = template.content.querySelector("[data-desc]");
        if (!titleNode || !descNode) {
            return;
        }

        activeSkill = skillId;
        clearActive();

        tiles.forEach(function (tile) {
            if (tile.getAttribute("data-skill") === skillId) {
                tile.classList.add("is-active");
                tile.setAttribute("aria-expanded", "true");
            }
        });

        titleEl.textContent = titleNode.textContent.trim();
        descEl.textContent = descNode.textContent.trim();

        if (placeholder) {
            placeholder.hidden = true;
        }
        body.hidden = false;
        detail.classList.add("is-open");
    }

    grid.addEventListener("click", function (event) {
        var tile = event.target.closest(".about-skill-tile");
        if (!tile || !grid.contains(tile)) {
            return;
        }

        var skillId = tile.getAttribute("data-skill");
        if (!skillId) {
            return;
        }

        if (activeSkill === skillId) {
            showPlaceholder();
            return;
        }

        showSkill(skillId);
    });
})();
