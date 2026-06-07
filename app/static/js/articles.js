document.addEventListener("DOMContentLoaded", function () {
    var PAGE_SIZE = 5;
    var currentCategory = "all";
    var currentQuery = "";
    var currentPage = 1;

    var items = Array.from(document.querySelectorAll(".article-item"));
    var pills = document.querySelectorAll(".tag-pill");
    var searchInput = document.getElementById("articles-search");
    var paginationEl = document.getElementById("pagination");
    var emptyEl = document.getElementById("articles-empty");

    function getFilteredItems() {
        var q = currentQuery.trim().toLowerCase();
        return items.filter(function (item) {
            var matchCategory =
                currentCategory === "all" || item.dataset.category === currentCategory;
            var matchSearch =
                !q ||
                item.dataset.title.toLowerCase().includes(q) ||
                item.dataset.excerpt.toLowerCase().includes(q) ||
                item.dataset.tags.toLowerCase().includes(q);
            return matchCategory && matchSearch;
        });
    }

    function buildPageNumbers(totalPages) {
        if (totalPages <= 5) {
            return Array.from({ length: totalPages }, function (_, i) {
                return i + 1;
            });
        }

        var pages = [1];
        var start = Math.max(2, currentPage - 1);
        var end = Math.min(totalPages - 1, currentPage + 1);

        if (start > 2) pages.push("...");
        for (var i = start; i <= end; i++) pages.push(i);
        if (end < totalPages - 1) pages.push("...");
        pages.push(totalPages);

        return pages;
    }

    function renderPagination(totalPages) {
        paginationEl.innerHTML = "";

        if (totalPages <= 1 && getFilteredItems().length === 0) {
            return;
        }

        var prevBtn = document.createElement("button");
        prevBtn.type = "button";
        prevBtn.className = "pagination-btn";
        prevBtn.textContent = "上一页";
        prevBtn.disabled = currentPage <= 1;
        prevBtn.addEventListener("click", function () {
            currentPage -= 1;
            render();
        });
        paginationEl.appendChild(prevBtn);

        buildPageNumbers(totalPages).forEach(function (page) {
            if (page === "...") {
                var ellipsis = document.createElement("span");
                ellipsis.className = "pagination-ellipsis";
                ellipsis.textContent = "...";
                paginationEl.appendChild(ellipsis);
                return;
            }

            var pageBtn = document.createElement("button");
            pageBtn.type = "button";
            pageBtn.className = "pagination-page" + (page === currentPage ? " active" : "");
            pageBtn.textContent = String(page);
            pageBtn.setAttribute("aria-label", "第 " + page + " 页");
            if (page === currentPage) {
                pageBtn.setAttribute("aria-current", "page");
            } else {
                (function (p) {
                    pageBtn.addEventListener("click", function () {
                        currentPage = p;
                        render();
                    });
                })(page);
            }
            paginationEl.appendChild(pageBtn);
        });

        var nextBtn = document.createElement("button");
        nextBtn.type = "button";
        nextBtn.className = "pagination-btn";
        nextBtn.textContent = "下一页";
        nextBtn.disabled = currentPage >= totalPages;
        nextBtn.addEventListener("click", function () {
            currentPage += 1;
            render();
        });
        paginationEl.appendChild(nextBtn);
    }

    function render() {
        var filtered = getFilteredItems();
        var totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));

        if (currentPage > totalPages) {
            currentPage = totalPages;
        }

        items.forEach(function (item) {
            item.style.display = "none";
        });

        var start = (currentPage - 1) * PAGE_SIZE;
        filtered.slice(start, start + PAGE_SIZE).forEach(function (item) {
            item.style.display = "";
        });

        emptyEl.hidden = filtered.length > 0;
        renderPagination(totalPages);
    }

    pills.forEach(function (pill) {
        pill.addEventListener("click", function () {
            pills.forEach(function (p) {
                p.classList.remove("active");
                p.setAttribute("aria-selected", "false");
            });
            pill.classList.add("active");
            pill.setAttribute("aria-selected", "true");
            currentCategory = pill.dataset.category;
            currentPage = 1;
            render();
        });
    });

    searchInput.addEventListener("input", function () {
        currentQuery = searchInput.value;
        currentPage = 1;
        render();
    });

    render();
});
