(function () {
    window.addEventListener('error', function () {
        document.documentElement.classList.add('js-failed');
    }, true);

    document.addEventListener('DOMContentLoaded', function () {
        injectScrollProgress();
        injectSkipLink();
        injectScrollToTop();
        injectNavBar();
        injectBreadcrumbs();
        injectFooter();
        markMaterialIconsAccessible();
        setupNavigation();
        setupNewsletter();
        setupRevealAnimations();
        setupHomepageFlow();
        setupLightbox();
        setupScrollProgress();
        setupMagneticButtons();
        setupParallaxImages();
        setupThreeThread();
        setupCounters();
        setupTestimonialSlider();
        setupProcessTabs();
        applySiteConfiguration();
    });

    function injectScrollProgress() {
        if (document.querySelector('.progress-line')) return;
        var bar = document.createElement('div');
        bar.className = 'progress-line';
        bar.setAttribute('aria-hidden', 'true');
        document.body.prepend(bar);
    }

    function injectSkipLink() {
        var skip = document.createElement('a');
        skip.href = '#main-content';
        skip.className = 'sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[120] focus:rounded-full focus:bg-primary focus:px-5 focus:py-3 focus:font-button-text focus:text-sm focus:text-white focus:shadow-lg focus:outline-none';
        skip.textContent = 'Skip to main content';
        document.body.insertBefore(skip, document.body.firstChild);
    }

    function injectScrollToTop() {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'scroll-btn';
        btn.setAttribute('aria-label', 'Scroll to top');
        btn.innerHTML = '<span class="material-symbols-outlined" style="font-size:20px;">keyboard_arrow_up</span>';
        btn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        document.body.appendChild(btn);

        var ticking = false;
        function update() {
            btn.classList.toggle('is-visible', window.scrollY > 520);
            ticking = false;
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                requestAnimationFrame(update);
                ticking = true;
            }
        }, { passive: true });
    }

    function injectNavBar() {
        var nav = document.querySelector('nav');
        if (!nav) return;
        nav.setAttribute('aria-label', 'Main navigation');

        var path = window.location.pathname;
        var page = path.substring(path.lastIndexOf('/') + 1) || 'index.html';

        function isActive(href) {
            if (href === 'index.html') return page === 'index.html' || page === '';
            return page === href;
        }

        var links = [
            { href: 'gallery.html', label: 'Gallery' },
            { href: 'how-it-works.html', label: 'How It Works' },
            { href: 'custom-order.html', label: 'Custom Order' },
            { href: 'about.html', label: 'About' }
        ];

        var desktopLinks = links.map(function (link) {
            var active = isActive(link.href);
            return '<a class="nav-link ' + (active ? 'is-active' : '') + '" href="' + link.href + '">' + link.label + '</a>';
        }).join('');

        var mobileLinks = links.map(function (link) {
            var active = isActive(link.href);
            return '<a class="block border-l-2 py-3 text-2xl font-display-lg leading-tight ' + (active ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant/60') + '" href="' + link.href + '">' + link.label + '</a>';
        }).join('');

        nav.className = 'rom-nav';
        nav.innerHTML =
            '<div class="container mx-auto flex h-16 md:h-20 items-center justify-between">' +
                '<a href="index.html" class="brand-mark brand-logo-link" aria-label="TSP Couture home"><img class="brand-logo brand-logo-small" src="assets/miniROM-nBG.png" alt="TSP Couture" draggable="false"/></a>' +
                '<div class="hidden items-center gap-8 md:flex">' + desktopLinks + '</div>' +
                '<div class="flex items-center gap-3">' +
                    '<a href="custom-order.html" class="hidden btn btn-primary magnetic sm:inline-flex">Begin Your Piece</a>' +
                    '<button id="mobile-menu-btn" class="inline-flex h-11 w-11 items-center justify-center rounded-full text-on-surface transition-colors hover:bg-primary/5 hover:text-primary md:hidden" aria-label="Toggle navigation menu" aria-expanded="false">' +
                        '<span class="material-symbols-outlined text-2xl" id="hamburger-icon">menu</span>' +
                    '</button>' +
                '</div>' +
            '</div>' +
            '<div id="mobile-drawer" class="drawer" aria-hidden="true" inert>' +
                '<div id="drawer-overlay" class="drawer-overlay"></div>' +
                '<div id="drawer-panel" class="drawer-panel">' +
                    '<div class="mb-8 flex items-center justify-between">' +
                        '<a href="index.html" class="brand-mark brand-logo-link"><img class="brand-logo brand-logo-small" src="assets/miniROM-nBG.png" alt="TSP Couture" draggable="false"/></a>' +
                        '<button id="drawer-close" class="inline-flex h-11 w-11 items-center justify-center rounded-full text-on-surface transition-colors hover:bg-primary/5 hover:text-primary" aria-label="Close menu"><span class="material-symbols-outlined text-2xl" aria-hidden="true">close</span></button>' +
                    '</div>' +
                    '<div class="flex flex-col gap-1">' + mobileLinks + '</div>' +
                    '<a href="custom-order.html" class="btn btn-primary magnetic mt-8 w-full">Begin Your Piece</a>' +
                    '<p class="mt-8 text-center font-label-caps text-[10px] uppercase tracking-[0.22em] text-on-surface-variant/45">New York · London · Lagos</p>' +
                '</div>' +
            '</div>';

        setupScrollNav();
    }

    function setupScrollNav() {
        var nav = document.querySelector('.rom-nav');
        if (!nav) return;
        var ticking = false;

        function update() {
            nav.classList.toggle('is-scrolled', window.scrollY > 48);
            ticking = false;
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                requestAnimationFrame(update);
                ticking = true;
            }
        }, { passive: true });
        update();
    }

    function setupNavigation() {
        var btn = document.getElementById('mobile-menu-btn');
        var drawer = document.getElementById('mobile-drawer');
        var panel = document.getElementById('drawer-panel');
        var overlay = document.getElementById('drawer-overlay');
        var close = document.getElementById('drawer-close');
        var icon = document.getElementById('hamburger-icon');
        if (!btn || !drawer || !panel || !overlay) return;

        function open() {
            drawer.classList.add('is-open');
            drawer.removeAttribute('inert');
            drawer.setAttribute('aria-hidden', 'false');
            document.body.classList.add('menu-open');
            btn.setAttribute('aria-expanded', 'true');
            if (icon) icon.textContent = 'close';
            if (window.gsap) {
                window.gsap.fromTo(panel, { x: 40, opacity: 0.96 }, { x: 0, opacity: 1, duration: 0.45, ease: 'power3.out' });
            }
        }

        function closeMenu() {
            drawer.classList.remove('is-open');
            drawer.setAttribute('aria-hidden', 'true');
            drawer.setAttribute('inert', '');
            document.body.classList.remove('menu-open');
            btn.setAttribute('aria-expanded', 'false');
            if (icon) icon.textContent = 'menu';
        }

        btn.addEventListener('click', function (event) {
            event.stopPropagation();
            drawer.classList.contains('is-open') ? closeMenu() : open();
        });

        if (close) close.addEventListener('click', closeMenu);
        overlay.addEventListener('click', closeMenu);

        drawer.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', closeMenu);
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && drawer.classList.contains('is-open')) closeMenu();
        });
    }

    function injectBreadcrumbs() {
        var main = document.querySelector('#main-content');
        if (!main) return;
        var path = window.location.pathname;
        var page = path.substring(path.lastIndexOf('/') + 1);
        if (!page || page === 'index.html' || page === '') return;

        var names = {
            'gallery.html': 'Gallery',
            'custom-order.html': 'Custom Order',
            'how-it-works.html': 'How It Works',
            'about.html': 'About',
            '404.html': 'Not Found'
        };

        var name = names[page];
        if (!name) return;

        var nav = document.createElement('nav');
        nav.setAttribute('aria-label', 'Breadcrumb');
        nav.className = 'container mx-auto px-0 py-4';
        nav.innerHTML = '<ol class="flex items-center gap-2 text-xs font-label-caps uppercase tracking-[0.18em] text-on-surface-variant/45">' +
            '<li><a href="index.html" class="transition-colors hover:text-primary">Home</a></li>' +
            '<li aria-hidden="true"><span class="material-symbols-outlined text-[10px]">chevron_right</span></li>' +
            '<li class="text-primary" aria-current="page">' + name + '</li>' +
            '</ol>';
        main.parentNode.insertBefore(nav, main);
    }

    function injectFooter() {
        var footer = document.querySelector('footer');
        if (!footer) return;

        footer.className = 'footer';
        footer.innerHTML =
            '<div class="container mx-auto px-0 py-14 md:py-20">' +
                '<div class="grid grid-cols-1 gap-10 md:grid-cols-12 md:gap-12">' +
                    '<div class="md:col-span-5">' +
                        '<a href="index.html" class="brand-mark brand-logo-link mb-5"><img class="brand-logo brand-logo-footer" src="assets/logomain-nBG.png" alt="TSP Couture" draggable="false"/></a>' +
                        '<p class="max-w-md text-sm leading-7 text-white/62">Bespoke tailoring for modern heritage: digitally guided, hand-finished, and made entirely for you.</p>' +
                        '<p class="mt-4 font-label-caps text-[10px] uppercase tracking-[0.22em] text-white/45">New York · London · Lagos</p>' +
                        '<div class="mt-6 flex gap-4" id="footer-socials"></div>' +
                    '</div>' +
                    '<div class="md:col-span-2">' +
                        '<h2 class="mb-5 font-label-caps text-[10px] uppercase tracking-[0.2em] text-primary-fixed-dim">Policies</h2>' +
                        '<ul class="space-y-3 text-sm">' +
                            '<li><a href="custom-order.html">No Returns Policy</a></li>' +
                            '<li><a href="how-it-works.html">Fitting & Payment</a></li>' +
                            '<li><a href="about.html">Atelier Standards</a></li>' +
                        '</ul>' +
                    '</div>' +
                    '<div class="md:col-span-2">' +
                        '<h2 class="mb-5 font-label-caps text-[10px] uppercase tracking-[0.2em] text-primary-fixed-dim">Explore</h2>' +
                        '<ul class="space-y-3 text-sm">' +
                            '<li><a href="gallery.html">Gallery</a></li>' +
                            '<li><a href="how-it-works.html">The Process</a></li>' +
                            '<li><a href="about.html">Our Story</a></li>' +
                        '</ul>' +
                    '</div>' +
                    '<div class="md:col-span-3">' +
                        '<h2 class="mb-5 font-label-caps text-[10px] uppercase tracking-[0.2em] text-primary-fixed-dim">Newsletter</h2>' +
                        '<p class="mb-4 text-sm leading-6 text-white/62">Lookbook notes, fabric stories, and private consultation windows.</p>' +
                        '<form id="newsletter-form" class="flex gap-2" novalidate>' +
                            '<input id="newsletter-email" class="min-w-0 flex-1 rounded-full border border-white/12 bg-white/8 px-4 py-3 text-sm text-ink placeholder:text-white/35 outline-none transition focus:border-primary-fixed-dim focus:ring-2 focus:ring-primary/20" placeholder="Email address" type="email" inputmode="email" pattern="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}" required aria-label="Email address" aria-describedby="newsletter-message" autocomplete="email"/>' +
                            '<button class="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary text-white transition hover:bg-primary-fixed-dim hover:text-primary-dark" aria-label="Subscribe"><span class="material-symbols-outlined text-lg">arrow_forward</span></button>' +
                        '</form>' +
                        '<span id="newsletter-message" class="mt-2 block text-xs text-white/50"></span>' +
                    '</div>' +
                '</div>' +
                '<div class="mt-14 flex flex-col gap-4 border-t border-white/10 pt-6 text-xs text-white/40 md:flex-row md:items-center md:justify-between">' +
                    '<p id="footer-copyright" class="text-white/60">&copy; 2026 TSP Couture. All rights reserved.</p>' +
                    '<div class="flex flex-wrap gap-5 font-label-caps uppercase tracking-[0.16em]"><span class="text-primary-fixed-dim">New York</span><span class="text-white/60">London</span><span class="text-white/60">Lagos</span></div>' +
                '</div>' +
            '</div>';
    }

    function markMaterialIconsAccessible() {
        document.querySelectorAll('.material-symbols-outlined').forEach(function (icon) {
            if (!icon.hasAttribute('aria-label')) {
                icon.setAttribute('aria-hidden', 'true');
            }
        });
    }

    function localApiBase() {
        var hostname = window.location.hostname || '';
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://127.0.0.1:8000';
        }
        return null;
    }

    function apiPath(path) {
        var base = window.TSP_COUTURE_API_BASE || localApiBase();
        if (base) {
            return base.replace(/\/$/, '') + path;
        }
        return null;
    }

    function setupNewsletter() {
        var form = document.getElementById('newsletter-form');
        var input = document.getElementById('newsletter-email');
        var msg = document.getElementById('newsletter-message');
        var utils = window.SecurityUtils;
        if (!form || !input || !msg) return;

        function isEmail(value) {
            if (utils && utils.validateEmail) return utils.validateEmail(value);
            return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value.trim());
        }

        function setMessage(text, isError) {
            msg.className = 'mt-2 block text-xs ' + (isError ? 'text-error' : 'text-primary-fixed-dim');
            utils.safeRender(msg, text || '');
        }

        input.addEventListener('input', function () {
            var value = input.value.trim();
            if (!value) {
                input.removeAttribute('aria-invalid');
                setMessage('');
                return;
            }

            var valid = isEmail(value);
            input.setAttribute('aria-invalid', valid ? 'false' : 'true');
            setMessage(valid ? '' : 'Please enter a valid email address.', !valid);
        });

        form.addEventListener('submit', function (event) {
            event.preventDefault();
            var email = input.value.trim();

            if (!isEmail(email)) {
                input.setAttribute('aria-invalid', 'true');
                input.focus();
                setMessage('Please enter a valid email address.', true);
                return;
            }

            input.setAttribute('aria-invalid', 'false');
            setMessage('Subscribing…');

            var endpoint = apiPath('/api/newsletter/subscribe/');
            if (!endpoint) {
                setMessage('Newsletter signup is ready for atelier-server integration.');
                input.value = '';
                return;
            }

            fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        if (!response.ok) throw new Error(data.error || 'Subscription failed');
                        return data;
                    });
                })
                .then(function (data) {
                    setMessage(data.message || 'Thank you for subscribing!');
                    input.value = '';
                })
                .catch(function (err) {
                    setMessage(err.message || 'Atelier server is offline. Please try again later.', true);
                });
        });
    }

    function setupRevealAnimations() {
        var elements = Array.from(document.querySelectorAll('[data-animate], .reveal, .reveal-left, .reveal-right, .reveal-scale'));
        if (!elements.length) return;

        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        function revealElement(el) {
            if (el.dataset.revealComplete) return;
            el.dataset.revealComplete = 'true';
            el.classList.add('is-visible');

            var delay = parseFloat(el.getAttribute('data-delay') || '0');
            if (window.gsap && !reduce) {
                window.gsap.fromTo(el, Object.assign({
                    autoAlpha: 0,
                    duration: 0.9,
                    delay: delay,
                    ease: 'power3.out',
                    overwrite: true
                }, getRevealFromValues(el)), {
                    autoAlpha: 1,
                    y: 0,
                    x: 0,
                    scale: 1,
                    duration: 0.9,
                    delay: delay,
                    ease: 'power3.out',
                    overwrite: true,
                    clearProps: 'transform,opacity'
                });
            }
        }

        if (!('IntersectionObserver' in window) || reduce) {
            elements.forEach(revealElement);
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    revealElement(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

        elements.forEach(function (el) { observer.observe(el); });
    }

    function getRevealFromValues(el) {
        if (el.classList.contains('reveal-left')) return { x: -34, y: 0 };
        if (el.classList.contains('reveal-right')) return { x: 34, y: 0 };
        if (el.classList.contains('reveal-scale')) return { y: 24, scale: 0.96 };
        return { y: 32 };
    }

    function setupHomepageFlow() {
        var isHome = window.location.pathname.split('/').pop().replace(/^$/, 'index.html') === 'index.html';
        if (!isHome) return;

        var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        setupScrollAwareMarquee(reduce);
        setupFlowSections(reduce);

        if (reduce || !window.gsap || !window.ScrollTrigger) return;

        window.ScrollTrigger.refresh();

        var hero = document.querySelector('.hero-shell');
        var heroCopy = document.querySelector('.hero-copy');
        var heroVisual = document.querySelector('.hero-visual');
        var scrollCue = document.querySelector('.scroll-cue');

        if (hero && heroCopy && heroVisual && scrollCue) {
            window.gsap.timeline({
                scrollTrigger: {
                    trigger: hero,
                    start: 'top top',
                    end: 'bottom top',
                    scrub: true,
                    invalidateOnRefresh: true
                }
            })
                .to(heroCopy, { yPercent: -3, ease: 'none' }, 0)
                .to(heroVisual, { x: 28, scale: 1.025, ease: 'none' }, 0)
                .to(scrollCue, { opacity: 0, y: -22, ease: 'none' }, 0);
        }

        var flowCards = Array.from(document.querySelectorAll('.flow-card'));
        flowCards.forEach(function (el, index) {
            var lift = 58 + (index % 3) * 8;
            window.gsap.fromTo(el, {
                autoAlpha: 0,
                y: lift,
                scale: 0.975
            }, {
                scrollTrigger: {
                    trigger: el,
                    start: 'top 88%',
                    end: 'bottom 64%',
                    scrub: 0.72,
                    invalidateOnRefresh: true
                },
                autoAlpha: 1,
                y: 0,
                scale: 1,
                duration: 0.9,
                ease: 'power3.out',
                clearProps: 'transform,opacity'
            });
        });
    }

    function setupScrollAwareMarquee(reduce) {
        var marquees = Array.from(document.querySelectorAll('[data-marquee]'));
        if (!marquees.length) return;

        marquees.forEach(function (marquee) {
            if (reduce) marquee.classList.add('is-reduced');
        });
        if (reduce) return;

        var lastY = window.scrollY || 0;
        var ticking = false;

        function update() {
            var nextY = window.scrollY || 0;
            var delta = nextY - lastY;
            var intensity = Math.min(1, Math.abs(delta) / 18);
            var duration = 34 - intensity * 18;

            marquees.forEach(function (marquee) {
                var track = marquee.querySelector('.marquee-track');
                if (!track) return;

                marquee.classList.toggle('is-scrolling', intensity > 0.05);
                marquee.classList.toggle('is-fast', intensity > 0.45);
                track.style.animationDuration = duration.toFixed(2) + 's';
                track.style.animationDirection = delta > 0 ? 'reverse' : 'normal';
            });

            lastY = nextY;
            ticking = false;
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                window.requestAnimationFrame(update);
                ticking = true;
            }
        }, { passive: true });

        marquees.forEach(function (marquee) {
            marquee.addEventListener('mouseenter', function () { marquee.classList.add('is-paused'); });
            marquee.addEventListener('mouseleave', function () { marquee.classList.remove('is-paused'); });
            marquee.addEventListener('focusin', function () { marquee.classList.add('is-paused'); });
            marquee.addEventListener('focusout', function () { marquee.classList.remove('is-paused'); });
        });

        update();
    }

    function setupFlowSections(reduce) {
        var sections = Array.from(document.querySelectorAll('[data-flow-section]'));
        if (!sections.length || reduce || !('IntersectionObserver' in window)) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                entry.target.classList.toggle('is-in-view', entry.isIntersecting);
            });
        }, { threshold: [0.16, 0.34, 0.58], rootMargin: '0px 0px -12% 0px' });

        sections.forEach(function (section) { observer.observe(section); });
    }

    function setupLightbox() {
        var dialog = document.getElementById('lightbox-dialog');
        if (!dialog) {
            dialog = document.createElement('dialog');
            dialog.id = 'lightbox-dialog';
            dialog.setAttribute('aria-label', 'Image lightbox');
            dialog.innerHTML = '<div class="relative flex min-h-screen items-center justify-center p-4"><img id="lightbox-img" src="" alt="" class="max-h-[88vh] max-w-[94vw] rounded-2xl object-contain shadow-cinema select-none"/><button id="lightbox-close" class="absolute right-4 top-4 inline-flex h-12 w-12 items-center justify-center rounded-full bg-white/90 text-on-surface backdrop-blur transition hover:bg-white" aria-label="Close image lightbox"><span class="material-symbols-outlined text-2xl" aria-hidden="true">close</span></button></div>';
            document.body.appendChild(dialog);
            markMaterialIconsAccessible();
        }

        var img = document.getElementById('lightbox-img');
        var closeBtn = document.getElementById('lightbox-close');

        function open(src, alt) {
            if (!img) return;
            img.src = src;
            img.alt = alt || 'Couture archive image';
            document.body.classList.add('menu-open');
            if (typeof dialog.showModal === 'function') {
                dialog.showModal();
            }
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', function () { dialog.close(); });
        }

        dialog.addEventListener('close', function () {
            document.body.classList.remove('menu-open');
            if (img) img.src = '';
        });

        dialog.addEventListener('click', function (event) {
            if (event.target === dialog) dialog.close();
        });

        document.body.addEventListener('click', function (event) {
            var target = event.target;
            if (!(target instanceof HTMLImageElement)) return;
            if (!target.classList.contains('cursor-zoom-in') && !target.closest('#gallery-grid') && !target.closest('.instagram-grid') && !target.closest('.image-frame')) return;
            event.preventDefault();
            event.stopPropagation();
            open(target.currentSrc || target.src, target.alt);
        }, true);
    }

    function setupScrollProgress() {
        var bar = document.querySelector('.progress-line');
        if (!bar) return;
        var ticking = false;

        function update() {
            var max = document.documentElement.scrollHeight - window.innerHeight;
            var progress = max > 0 ? window.scrollY / max : 0;
            bar.style.transform = 'scaleX(' + Math.max(0, Math.min(1, progress)) + ')';
            ticking = false;
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                requestAnimationFrame(update);
                ticking = true;
            }
        }, { passive: true });
        update();
    }

    function setupMagneticButtons() {
        if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) return;
        document.querySelectorAll('.magnetic').forEach(function (el) {
            el.addEventListener('pointermove', function (event) {
                var rect = el.getBoundingClientRect();
                var x = event.clientX - rect.left - rect.width / 2;
                var y = event.clientY - rect.top - rect.height / 2;
                el.style.transform = 'translate(' + x * 0.16 + 'px, ' + y * 0.22 + 'px)';
            });
            el.addEventListener('pointerleave', function () {
                el.style.transform = '';
            });
        });
    }

    function setupParallaxImages() {
        document.querySelectorAll('[data-parallax]').forEach(function (el) {
            var speed = parseFloat(el.getAttribute('data-parallax') || '0.08');
            var ticking = false;

            function update() {
                var rect = el.getBoundingClientRect();
                if (rect.bottom < 0 || rect.top > window.innerHeight) {
                    ticking = false;
                    return;
                }
                var offset = (window.innerHeight / 2 - (rect.top + rect.height / 2)) * speed;
                el.style.transform = 'translate3d(0, ' + offset.toFixed(2) + 'px, 0)';
                ticking = false;
            }

            window.addEventListener('scroll', function () {
                if (!ticking) {
                    requestAnimationFrame(update);
                    ticking = true;
                }
            }, { passive: true });
            update();
        });
    }

    function setupThreeThread() {
        var canvas = document.getElementById('thread-canvas');
        if (!canvas || !window.THREE) return;

        var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.setClearColor(0x000000, 0);

        var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
        camera.position.z = 5;

        var group = new THREE.Group();
        scene.add(group);

        var count = 128;
        var pointData = [];
        var lineData = [];

        for (var i = 0; i < count; i++) {
            var angle = (i / count) * Math.PI * 2;
            var radius = 1.25 + Math.random() * 1.35;
            var point = new THREE.Vector3(
                Math.cos(angle) * radius + (Math.random() - 0.5) * 0.45,
                Math.sin(angle) * radius + (Math.random() - 0.5) * 0.45,
                (Math.random() - 0.5) * 1.4
            );
            pointData.push(point.x, point.y, point.z);
        }

        for (var j = 0; j < count; j++) {
            var a = j * 3;
            var b = ((j + 17 + Math.floor(Math.random() * 24)) % count) * 3;
            lineData.push(pointData[a], pointData[a + 1], pointData[a + 2], pointData[b], pointData[b + 1], pointData[b + 2]);
        }

        var pointsGeometry = new THREE.BufferGeometry();
        pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(pointData, 3));
        var pointsMaterial = new THREE.PointsMaterial({
            color: 0x914325,
            size: 0.018,
            transparent: true,
            opacity: 0.62,
            depthWrite: false
        });
        var points = new THREE.Points(pointsGeometry, pointsMaterial);
        group.add(points);

        var lineGeometry = new THREE.BufferGeometry();
        lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(lineData, 3));
        var lineMaterial = new THREE.LineBasicMaterial({
            color: 0x914325,
            transparent: true,
            opacity: 0.18,
            depthWrite: false
        });
        var lines = new THREE.LineSegments(lineGeometry, lineMaterial);
        group.add(lines);

        function resize() {
            var parent = canvas.parentElement;
            var rect = parent ? parent.getBoundingClientRect() : canvas.getBoundingClientRect();
            var width = Math.max(1, Math.floor(rect.width));
            var height = Math.max(1, Math.floor(rect.height));
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height, false);
        }

        var frame = 0;
        function animate() {
            frame += 0.004;
            group.rotation.z = Math.sin(frame) * 0.08;
            group.rotation.y = Math.cos(frame * 0.8) * 0.12;
            points.rotation.x = frame * 0.12;
            lines.rotation.x = -frame * 0.08;
            renderer.render(scene, camera);
            requestAnimationFrame(animate);
        }

        resize();
        window.addEventListener('resize', resize);
        animate();
    }

    function setupCounters() {
        var counters = Array.from(document.querySelectorAll('[data-count]'));
        if (!counters.length) return;

        if (!('IntersectionObserver' in window)) {
            counters.forEach(runCounter);
            return;
        }

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    runCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(function (counter) { observer.observe(counter); });
    }

    function runCounter(el) {
        var target = Number(el.getAttribute('data-count') || '0');
        var suffix = el.getAttribute('data-suffix') || '';
        var duration = 1100;
        var start = null;

        function tick(now) {
            if (!start) start = now;
            var progress = Math.min((now - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * eased) + suffix;
            if (progress < 1) requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
    }

    function setupTestimonialSlider() {
        var carousel = document.getElementById('testimonial-carousel');
        var dots = document.getElementById('carousel-dots');
        if (!carousel || !dots) return;

        var quoteSlides = Array.from(carousel.querySelectorAll('p[data-slide]'));
        var citeSlides = Array.from(carousel.querySelectorAll('cite[data-slide]'));
        var slideGroups = quoteSlides.map(function (quote, index) {
            return citeSlides[index] ? [quote, citeSlides[index]] : [quote];
        });
        var slides = slideGroups.flat();
        var buttons = Array.from(dots.querySelectorAll('button'));
        var current = 0;
        var timer = null;

        function show(index) {
            current = (index + slideGroups.length) % slideGroups.length;
            slides.forEach(function (slide) {
                slide.classList.remove('is-active');
                slide.classList.add('hidden');
                slide.setAttribute('aria-hidden', 'true');
            });
            slideGroups[current].forEach(function (slide) {
                slide.classList.add('is-active');
                slide.classList.remove('hidden');
                slide.setAttribute('aria-hidden', 'false');
            });
            buttons.forEach(function (button, i) {
                button.classList.toggle('is-active', i === current);
                button.setAttribute('aria-selected', i === current ? 'true' : 'false');
            });
        }

        function next() {
            show(current + 1);
        }

        buttons.forEach(function (button, i) {
            button.addEventListener('click', function () { show(i); restart(); });
        });

        function restart() {
            if (timer) clearInterval(timer);
            timer = setInterval(next, 6500);
        }

        carousel.addEventListener('mouseenter', function () { if (timer) clearInterval(timer); });
        carousel.addEventListener('mouseleave', restart);
        show(0);
        restart();
    }

    function setupProcessTabs() {
        var steps = Array.from(document.querySelectorAll('.process-step'));
        var panels = Array.from(document.querySelectorAll('[data-process-panel]'));
        if (!steps.length || !panels.length) return;

        function activate(index) {
            steps.forEach(function (step, i) {
                step.classList.toggle('is-active', i === index);
                step.setAttribute('aria-selected', i === index ? 'true' : 'false');
            });
            panels.forEach(function (panel, i) {
                panel.classList.toggle('is-active', i === index);
                panel.classList.toggle('hidden', i !== index);
                panel.setAttribute('aria-hidden', i === index ? 'false' : 'true');
            });
        }

        steps.forEach(function (step, index) {
            step.addEventListener('click', function () { activate(index); });
            step.addEventListener('keydown', function (event) {
                if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
                    event.preventDefault();
                    steps[(index + 1) % steps.length].focus();
                    activate((index + 1) % steps.length);
                }
                if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
                    event.preventDefault();
                    var prev = (index - 1 + steps.length) % steps.length;
                    steps[prev].focus();
                    activate(prev);
                }
            });
        });

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    var index = steps.indexOf(entry.target);
                    if (index !== -1) activate(index);
                    observer.unobserve(entry.target);
                });
            }, { threshold: 0.35, rootMargin: '-18% 0px -35% 0px' });

            steps.forEach(function (step) { observer.observe(step); });
        }
    }

    function applySiteConfiguration() {
        var endpoint = apiPath('/api/site-config/');
        if (!endpoint) return;

        fetch(endpoint)
            .then(function (response) {
                if (!response.ok) throw new Error('Site configuration unavailable');
                return response.json();
            })
            .then(function (cfg) {
                var utils = window.SecurityUtils;
                if (cfg.hero_tagline) {
                    var heroTagline = document.getElementById('hero-tagline');
                    if (heroTagline) utils.safeRender(heroTagline, cfg.hero_tagline);
                }
                if (cfg.hero_subtext) {
                    var heroSubtext = document.getElementById('hero-subtext');
                    if (heroSubtext) utils.safeRender(heroSubtext, cfg.hero_subtext);
                }
                if (cfg.delivery_lead_time) {
                    var deliveryTime = document.getElementById('delivery-lead-time');
                    if (deliveryTime) utils.safeRender(deliveryTime, 'Delivered in a luxury keepsake box, ' + cfg.delivery_lead_time + '.');
                }
                if (cfg.footer_copyright) {
                    var copyright = document.getElementById('footer-copyright');
                    if (copyright) utils.safeRender(copyright, cfg.footer_copyright);
                }
                if (cfg.footer_address) {
                    var address = document.getElementById('footer-address');
                    if (address) utils.safeRender(address, cfg.footer_address);
                }
                var socialContainer = document.getElementById('footer-socials');
                if (socialContainer) {
                    socialContainer.innerHTML = '';
                    var socials = [
                        ['instagram', cfg.instagram_url],
                        ['facebook', cfg.facebook_url],
                        ['twitter', cfg.twitter_url],
                        ['pinterest', cfg.pinterest_url]
                    ];
                    socials.forEach(function (item) {
                        var label = item[0];
                        var url = item[1];
                        if (!url) return;
                        var a = document.createElement('a');
                        a.href = url;
                        a.target = '_blank';
                        a.rel = 'noopener';
                        a.className = 'inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-white/8 text-white/70 transition hover:border-primary-fixed-dim hover:bg-primary-fixed-dim hover:text-primary-dark';
                        a.setAttribute('aria-label', label);
                        a.textContent = label.slice(0, 1).toUpperCase();
                        socialContainer.appendChild(a);
                    });
                }
            })
            .catch(function () {});
    }
})();
