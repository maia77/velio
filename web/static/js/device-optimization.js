/* ===== تحسينات خاصة بالأجهزة المختلفة ===== */

// كشف نوع الجهاز
const DeviceDetector = {
  isMobile: () => window.innerWidth <= 768,
  isTablet: () => window.innerWidth > 768 && window.innerWidth <= 1024,
  isDesktop: () => window.innerWidth > 1024,
  isTouch: () => 'ontouchstart' in window || navigator.maxTouchPoints > 0,
  isIOS: () => /iPad|iPhone|iPod/.test(navigator.userAgent),
  isAndroid: () => /Android/.test(navigator.userAgent),
  isSafari: () => /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent)
};

// تحسينات الأداء
const PerformanceOptimizer = {
  // تحسين التمرير
  optimizeScrolling: () => {
    if (DeviceDetector.isMobile()) {
      document.body.style.webkitOverflowScrolling = 'touch';
      document.body.style.overscrollBehavior = 'contain';
    }
  },

  // تحسين الصور
  optimizeImages: () => {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      img.style.webkitBackfaceVisibility = 'hidden';
      img.style.backfaceVisibility = 'hidden';
      img.style.imageRendering = 'crisp-edges';
    });
  },

  // تحسين العناصر المتحركة
  optimizeAnimations: () => {
    if (DeviceDetector.isMobile()) {
      const animatedElements = document.querySelectorAll('.product-card, .feature-card, .btn-primary, .btn-outline');
      animatedElements.forEach(el => {
        el.style.willChange = 'transform';
        el.style.webkitTransform = 'translateZ(0)';
        el.style.transform = 'translateZ(0)';
      });
    }
  },

  // تحسين الذاكرة
  optimizeMemory: () => {
    if (DeviceDetector.isMobile()) {
      // إزالة التأثيرات على الهواتف لتوفير الذاكرة
      const hoverElements = document.querySelectorAll('.product-card:hover, .feature-card:hover');
      hoverElements.forEach(el => {
        el.style.transform = 'none';
      });
    }
  }
};

// تحسينات اللمس
const TouchOptimizer = {
  // تحسين الأزرار لللمس
  optimizeButtons: () => {
    const buttons = document.querySelectorAll('button, .btn, .nav-link, .mobile-bottom-nav .nav-item');
    buttons.forEach(btn => {
      btn.style.webkitTapHighlightColor = 'transparent';
      btn.style.touchAction = 'manipulation';
      btn.style.userSelect = 'none';
      btn.style.minHeight = '44px';
      btn.style.minWidth = '44px';
    });
  },

  // تحسين حقول الإدخال
  optimizeInputs: () => {
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      input.style.webkitAppearance = 'none';
      input.style.mozAppearance = 'none';
      input.style.appearance = 'none';
      input.style.webkitTapHighlightColor = 'transparent';
      input.style.fontSize = '16px'; // منع التكبير في iOS
    });
  },

  // تحسين الروابط
  optimizeLinks: () => {
    const links = document.querySelectorAll('a, .nav-link');
    links.forEach(link => {
      link.style.webkitTapHighlightColor = 'transparent';
      link.style.touchAction = 'manipulation';
      link.style.userSelect = 'none';
    });
  }
};

// تحسينات إمكانية الوصول
const AccessibilityOptimizer = {
  // تحسين التباين
  optimizeContrast: () => {
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      const productCards = document.querySelectorAll('.product-card');
      productCards.forEach(card => {
        card.style.border = '2px solid #333';
      });
    }
  },

  // تحسين الحركة
  optimizeMotion: () => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      const style = document.createElement('style');
      style.textContent = `
        * {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
        }
      `;
      document.head.appendChild(style);
    }
  }
};

// تحسينات شريط التنقل السفلي
const MobileNavigationOptimizer = {
  // تحديث عداد السلة
  updateCartCount: async (count) => {
    const mobileCartCount = document.getElementById('mobile-cart-count');
    if (mobileCartCount) {
      mobileCartCount.textContent = count || 0;
    }
  },

  // تحسين التفاعل
  optimizeInteraction: () => {
    const navItems = document.querySelectorAll('.mobile-bottom-nav .nav-item');
    navItems.forEach(item => {
      item.addEventListener('touchstart', (e) => {
        e.target.style.transform = 'scale(0.95)';
        e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
      });

      item.addEventListener('touchend', (e) => {
        setTimeout(() => {
          e.target.style.transform = 'scale(1)';
          e.target.style.backgroundColor = 'transparent';
        }, 150);
      });
    });
  }
};

// تحسينات التحميل
const LoadingOptimizer = {
  // تحميل تدريجي للصور
  lazyLoadImages: () => {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy-load');
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    });

    images.forEach(img => imageObserver.observe(img));
  },

  // تحسين الخطوط
  optimizeFonts: () => {
    if (DeviceDetector.isMobile()) {
      document.body.style.webkitFontSmoothing = 'antialiased';
      document.body.style.mozOsxFontSmoothing = 'grayscale';
      document.body.style.textRendering = 'optimizeLegibility';
    }
  }
};

// تحسينات الاستجابة
const ResponsiveOptimizer = {
  // تحديث التخطيط عند تغيير حجم الشاشة
  updateLayout: () => {
    const updateLayout = () => {
      if (DeviceDetector.isMobile()) {
        // تحسينات للهواتف
        document.body.classList.add('mobile-layout');
        document.body.classList.remove('tablet-layout', 'desktop-layout');
      } else if (DeviceDetector.isTablet()) {
        // تحسينات للأجهزة اللوحية
        document.body.classList.add('tablet-layout');
        document.body.classList.remove('mobile-layout', 'desktop-layout');
      } else {
        // تحسينات لأجهزة الكمبيوتر
        document.body.classList.add('desktop-layout');
        document.body.classList.remove('mobile-layout', 'tablet-layout');
      }
    };

    updateLayout();
    window.addEventListener('resize', updateLayout);
  },

  // تحسين الشبكة
  optimizeGrid: () => {
    const productsGrid = document.querySelector('.products-grid');
    if (productsGrid) {
      if (DeviceDetector.isMobile()) {
        productsGrid.style.gridTemplateColumns = '1fr';
      } else if (DeviceDetector.isTablet()) {
        productsGrid.style.gridTemplateColumns = 'repeat(2, 1fr)';
      } else {
        productsGrid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(300px, 1fr))';
      }
    }
  }
};

// تهيئة جميع التحسينات
const initializeOptimizations = () => {
  // تحسينات الأداء
  PerformanceOptimizer.optimizeScrolling();
  PerformanceOptimizer.optimizeImages();
  PerformanceOptimizer.optimizeAnimations();
  PerformanceOptimizer.optimizeMemory();

  // تحسينات اللمس
  TouchOptimizer.optimizeButtons();
  TouchOptimizer.optimizeInputs();
  TouchOptimizer.optimizeLinks();

  // تحسينات إمكانية الوصول
  AccessibilityOptimizer.optimizeContrast();
  AccessibilityOptimizer.optimizeMotion();

  // تحسينات شريط التنقل السفلي
  MobileNavigationOptimizer.optimizeInteraction();

  // تحسينات التحميل
  LoadingOptimizer.lazyLoadImages();
  LoadingOptimizer.optimizeFonts();

  // تحسينات الاستجابة
  ResponsiveOptimizer.updateLayout();
  ResponsiveOptimizer.optimizeGrid();
};

// تشغيل التحسينات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', initializeOptimizations);

// تشغيل التحسينات عند تغيير حجم النافذة
window.addEventListener('resize', () => {
  ResponsiveOptimizer.updateLayout();
  ResponsiveOptimizer.optimizeGrid();
});

// تصدير الوظائف للاستخدام في ملفات أخرى
window.DeviceDetector = DeviceDetector;
window.PerformanceOptimizer = PerformanceOptimizer;
window.TouchOptimizer = TouchOptimizer;
window.AccessibilityOptimizer = AccessibilityOptimizer;
window.MobileNavigationOptimizer = MobileNavigationOptimizer;
window.LoadingOptimizer = LoadingOptimizer;
window.ResponsiveOptimizer = ResponsiveOptimizer;
