// ===== شريط التنقل السفلي المتحرك =====

let lastScrollTop = 0;
let isScrolling = false;

// دالة لجعل الشريط يتحرك مع التمرير
function handleScroll() {
  const bottomNav = document.querySelector('.mobile-bottom-nav');
  if (!bottomNav) return;
  
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  
  // إخفاء الشريط عند التمرير لأسفل
  if (scrollTop > lastScrollTop && scrollTop > 100) {
    bottomNav.style.transform = 'translateY(100%)';
  } else {
    // إظهار الشريط عند التمرير لأعلى
    bottomNav.style.transform = 'translateY(0)';
  }
  
  lastScrollTop = scrollTop;
}

// إضافة مستمع التمرير
window.addEventListener('scroll', function() {
  if (!isScrolling) {
    window.requestAnimationFrame(function() {
      handleScroll();
      isScrolling = false;
    });
    isScrolling = true;
  }
});

// إعداد الشريط عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
  const bottomNav = document.querySelector('.mobile-bottom-nav');
  
  if (bottomNav) {
    // إضافة transition للحركة السلسة
    bottomNav.style.transition = 'transform 0.3s ease-in-out';
    
    // ضمان إظهار الشريط في البداية
    bottomNav.style.transform = 'translateY(0)';
  }
});

// إظهار الشريط عند التمرير لأعلى
window.addEventListener('scroll', function() {
  const bottomNav = document.querySelector('.mobile-bottom-nav');
  if (!bottomNav) return;
  
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  
  if (scrollTop < lastScrollTop) {
    bottomNav.style.transform = 'translateY(0)';
  }
  
  lastScrollTop = scrollTop;
});
