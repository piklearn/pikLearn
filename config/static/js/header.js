/**
 * Glassmorphism Header Controller
 * Handles scroll behavior, search autocomplete, and theme interactions
 */

(function() {
    'use strict';

    // ============================================================
    // 1. DOM REFERENCES
    // ============================================================
    const header = document.getElementById('mainHeader');
    const heroSection = document.getElementById('heroSection');
    const searchToggle = document.querySelector('.search-toggle');
    const searchCollapse = document.getElementById('searchCollapse');
    const themeToggle = document.getElementById('themeToggle');
    
    // Hero Search (Homepage)
    const heroSearchInput = document.getElementById('heroSearchInput');
    const heroSearchBtn = document.getElementById('heroSearchBtn');
    const heroResultsContainer = document.getElementById('heroAutocompleteResults');
    
    // Header Search (Other pages)
    const headerSearchInput = document.getElementById('headerSearchInput');
    const headerSearchBtn = document.getElementById('headerSearchBtn');
    const headerResultsContainer = document.getElementById('headerAutocompleteResults');

    // ============================================================
    // 2. SCROLL BEHAVIOR
    // ============================================================
    let lastScrollY = window.scrollY;
    let isHeaderHidden = false;
    let hideThreshold = 80;
    let showThreshold = 20;
    let ticking = false;

    function handleScroll() {
        const currentScrollY = window.scrollY;
        const scrollDelta = currentScrollY - lastScrollY;
        const isScrollingDown = scrollDelta > 0;

        // اگر در بخش hero هستیم، هدر را مخفی نکن
        if (heroSection) {
            const heroRect = heroSection.getBoundingClientRect();
            const heroBottom = heroRect.bottom;
            if (heroBottom > 0 && currentScrollY < heroRect.height) {
                if (isHeaderHidden) {
                    showHeader();
                }
                lastScrollY = currentScrollY;
                return;
            }
        }

        // تصمیم‌گیری برای مخفی یا نمایش هدر
        if (isScrollingDown && !isHeaderHidden && currentScrollY > hideThreshold) {
            hideHeader();
        } else if (!isScrollingDown && isHeaderHidden && Math.abs(scrollDelta) > showThreshold) {
            showHeader();
        }

        // اگر در بالای صفحه هستیم، هدر را نشان بده
        if (currentScrollY <= 10 && isHeaderHidden) {
            showHeader();
        }

        lastScrollY = currentScrollY;
    }

    function hideHeader() {
        if (isHeaderHidden) return;
        isHeaderHidden = true;
        header.classList.remove('header-visible');
        header.classList.add('header-hidden');
        
        // بستن search اگر باز باشد
        if (searchCollapse && searchCollapse.classList.contains('show')) {
            const bsCollapse = bootstrap.Collapse.getInstance(searchCollapse);
            if (bsCollapse) bsCollapse.hide();
        }
    }

    function showHeader() {
        if (!isHeaderHidden) return;
        isHeaderHidden = false;
        header.classList.remove('header-hidden');
        header.classList.add('header-visible');
    }

    // ============================================================
    // 3. SEARCH AUTOCOMPLETE CORE
    // ============================================================
    let searchTimeout = null;

    function performSearch(query, resultsContainer, inputElement) {
        if (!query || query.length < 2) {
            hideResults(resultsContainer);
            return;
        }

        showLoading(resultsContainer);

        // دریافت CSRF token
        const csrfToken = getCsrfToken();

        const url = `/courses/course-autocomplete/?query=${encodeURIComponent(query)}`;

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken || '',
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            let results = [];
            
            // بررسی ساختار داده
            if (data.results) {
                results = data.results;
            } else if (Array.isArray(data)) {
                results = data;
            } else if (data.data) {
                results = data.data;
            }
            
            displayResults(results, resultsContainer);
        })
        .catch(error => {
            console.error('Search error:', error);
            showError(resultsContainer);
        });
    }

    function displayResults(results, container) {
        if (!container) return;

        if (!results || results.length === 0) {
            container.innerHTML = `
                <div class="autocomplete-empty">
                    <i class="bi bi-search"></i>
                    <p>نتیجه‌ای یافت نشد</p>
                    <small style="opacity: 0.6;">سعی کنید با کلمات دیگر جستجو کنید</small>
                </div>
            `;
            container.classList.add('show');
            return;
        }

        let html = '';
        results.forEach(item => {
            const id = item.id || item.pk || '';
            const title = item.title || item.text || item.name || 'بدون عنوان';
            const subtitle = item.subtitle || item.description || item.subtext || '';
            const price = item.price || item.cost || '';
            const url = item.url || item.link || `/courses/${id}/`;
            
            let priceHtml = '';
            if (price) {
                priceHtml = `<span class="result-price">${price} تومان</span>`;
            } else if (item.is_free || item.free) {
                priceHtml = `<span class="result-badge">رایگان</span>`;
            } else {
                priceHtml = `<span class="result-badge">دوره</span>`;
            }
            
            html += `
                <a href="${url}" class="autocomplete-result-item">
                    <span class="result-icon">📘</span>
                    <div class="result-content">
                        <div class="result-title">${escapeHtml(title)}</div>
                        ${subtitle ? `<div class="result-subtitle">${escapeHtml(subtitle)}</div>` : ''}
                    </div>
                    ${priceHtml}
                </a>
            `;
        });

        container.innerHTML = html;
        container.classList.add('show');
    }

    function showLoading(container) {
        if (!container) return;
        container.innerHTML = `
            <div class="autocomplete-loading">
                <div class="spinner"></div>
                <span>در حال جستجو...</span>
            </div>
        `;
        container.classList.add('show');
    }

    function showError(container) {
        if (!container) return;
        container.innerHTML = `
            <div class="autocomplete-empty">
                <i class="bi bi-exclamation-triangle"></i>
                <p>خطا در جستجو</p>
                <small style="opacity: 0.6;">لطفاً دوباره تلاش کنید</small>
            </div>
        `;
        container.classList.add('show');
    }

    function hideResults(container) {
        if (container) {
            container.classList.remove('show');
        }
    }

    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(unsafe).replace(/[&<>"']/g, function(m) {
            return map[m];
        });
    }

    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('input[name="csrfmiddlewaretoken"]')?.value ||
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        return token || '';
    }

    // ============================================================
    // 4. SETUP SEARCH FOR SPECIFIC INPUT
    // ============================================================
    function setupSearch(input, button, resultsContainer) {
        if (!input) return;

        // Input handler with debounce
        input.addEventListener('input', function(e) {
            const query = this.value.trim();
            
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }

            if (!query || query.length < 2) {
                hideResults(resultsContainer);
                return;
            }

            showLoading(resultsContainer);

            searchTimeout = setTimeout(() => {
                performSearch(query, resultsContainer, input);
            }, 300);
        });

        // Keyboard navigation
        input.addEventListener('keydown', function(e) {
            // ESC: close results
            if (e.key === 'Escape') {
                hideResults(resultsContainer);
                this.blur();
                return;
            }
            
            // Enter: search
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = this.value.trim();
                if (query.length >= 2) {
                    performSearch(query, resultsContainer, input);
                }
                return;
            }

            // Arrow keys: navigate results
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                const items = resultsContainer?.querySelectorAll('.autocomplete-result-item');
                if (!items || items.length === 0) return;
                
                let currentIndex = -1;
                items.forEach((item, index) => {
                    if (item.classList.contains('active')) {
                        currentIndex = index;
                        item.classList.remove('active');
                    }
                });
                
                if (e.key === 'ArrowDown') {
                    currentIndex = Math.min(currentIndex + 1, items.length - 1);
                } else {
                    currentIndex = Math.max(currentIndex - 1, 0);
                }
                
                if (items[currentIndex]) {
                    items[currentIndex].classList.add('active');
                    items[currentIndex].scrollIntoView({ block: 'nearest' });
                }
            }
        });

        // Focus: show results if there's a query
        input.addEventListener('focus', function() {
            const query = this.value.trim();
            if (query.length >= 2) {
                performSearch(query, resultsContainer, input);
            }
        });

        // Blur: hide results after short delay
        input.addEventListener('blur', function() {
            setTimeout(() => {
                hideResults(resultsContainer);
            }, 200);
        });

        // Button click
        if (button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const query = input.value.trim();
                if (query && query.length >= 2) {
                    performSearch(query, resultsContainer, input);
                } else {
                    input.focus();
                }
            });
        }
    }

    // ============================================================
    // 5. CLOSE RESULTS ON OUTSIDE CLICK
    // ============================================================
    document.addEventListener('click', function(e) {
        // Hero results
        if (heroResultsContainer && !heroResultsContainer.contains(e.target) && 
            heroSearchInput && !heroSearchInput.contains(e.target) &&
            heroSearchBtn && !heroSearchBtn.contains(e.target)) {
            hideResults(heroResultsContainer);
        }
        
        // Header results
        if (headerResultsContainer && !headerResultsContainer.contains(e.target) && 
            headerSearchInput && !headerSearchInput.contains(e.target) &&
            headerSearchBtn && !headerSearchBtn.contains(e.target)) {
            hideResults(headerResultsContainer);
        }
    });

    // ============================================================
    // 6. THEME TOGGLE
    // ============================================================
    if (themeToggle) {
        // اگر toggle از نوع glass-icon-btn نیست
        if (!themeToggle.classList.contains('glass-icon-btn')) {
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-bs-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-bs-theme', newTheme);
                
                try {
                    localStorage.setItem('theme', newTheme);
                } catch (e) {
                    // خطای ذخیره‌سازی را نادیده بگیر
                }
            });
        }
    }

    // ============================================================
    // 7. INITIALIZATION
    // ============================================================
    
    // Setup search for hero (homepage)
    setupSearch(heroSearchInput, heroSearchBtn, heroResultsContainer);
    
    // Setup search for header (other pages)
    setupSearch(headerSearchInput, headerSearchBtn, headerResultsContainer);

    // Set initial header state
    if (window.scrollY <= 10) {
        header.classList.add('header-visible');
    } else {
        header.classList.add('header-hidden');
    }

    // Throttled scroll listener
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                handleScroll();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            // اگر نیاز به تنظیمات خاصی دارید
        }, 250);
    }, { passive: true });

    // ============================================================
    // 8. CONSOLE LOG
    // ============================================================
    console.log('✨ Glassmorphism Header initialized');
    console.log('🔍 Search autocomplete ready');

})();